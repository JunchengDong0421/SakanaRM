import json
import threading
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from .cdn_utils import SakanaCDNClient
from .llm_utils import SimpleKeywordClient
from .macros import *
from .models import Paper, Tag, SakanaUser, Workflow


def home_page(request):
    uid = request.session.get("uid")
    # only display 10 most recent workflows on homepage
    workflows = Workflow.objects.filter(user_id=uid, is_archived=False)[:10]
    return render(request, "core/index.html", {"workflows": workflows})


@login_required()
def upload_paper_page(request):
    return render(request, "core/paper_upload.html", {"UPLOAD": UPLOAD})


@login_required()
def process_paper_page(request):
    uid = request.session.get("uid")
    selected_pid = request.GET.get("selectedPid")
    papers = Paper.objects.filter(owner_id=uid)
    selected_paper = papers.filter(id=selected_pid).first()
    if not selected_paper or selected_pid is None:
        selected_pid = -1
    tags = Tag.objects.all()
    return render(request, "core/paper_process.html", {"papers": papers, "tags": tags, "PROCESS": PROCESS,
                                                       "selected_pid": int(selected_pid)})


class PaperDetailView(DetailView):
    model = Paper


class PaperUserListView(ListView):
    model = SakanaUser  # in the url, we want uid as parameter, not pid
    paginate_by = 10
    template_name = "core/paper_user_list.html"

    def get_queryset(self):
        uid = self.request.session.get("uid")
        return Paper.objects.filter(owner_id=uid)


class WorkflowDetailView(DetailView):
    model = Workflow

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workflow = Workflow.objects.filter(id=self.kwargs['pk']).first()
        if workflow:
            context["result"] = json.loads(workflow.result)
            context["pending"] = PENDING
            context["completed"] = COMPLETED
            context["upload"] = UPLOAD
            context["process"] = PROCESS
            context["can_abort_status"] = CAN_ABORT_STATUS
        return context


def start_workflow_task(request, wid, file_obj):
    workflow = Workflow.objects.filter(id=wid).first()
    if not workflow:
        return
    try:
        uid = request.session.get('uid')
        title = request.POST.get("title")

        work_type = int(req_type) if (req_type := request.POST.get("type")).isnumeric() else -1
        if work_type == UPLOAD:
            paper = Paper.objects.filter(title=title, owner_id=uid).first()
            if not paper:
                return

            # in case of caching, re-query
            workflow = Workflow.objects.filter(id=wid).first()
            if not workflow or workflow.status == ABORTED:
                return
            workflow.stage = S_UPLOADING
            workflow.save()

            cdn_client = SakanaCDNClient()
            replace = not not request.POST.get("replace")
            if not replace:
                file_path = cdn_client.store_paper(file_obj)
            else:
                filepath = paper.file_path
                file_path = cdn_client.replace_paper(filepath, file_obj)

            # in case of caching, re-query
            workflow = Workflow.objects.filter(id=wid).first()
            # if workflow is aborted or deleted (not allowed for users)
            if not workflow or workflow.status == ABORTED:
                _ = cdn_client.delete_paper(file_path)  # delete new paper
                paper = Paper.objects.filter(title=title, owner_id=uid).first()
                if not paper:  # if paper is deleted
                    return
                if not paper.file_path:  # delete paper entry
                    paper.delete()
                return
            # else
            paper = Paper.objects.filter(title=title, owner_id=uid).first()
            if not paper:  # if paper is deleted or altered during normal workflow execution
                workflow.result = json.dumps({**json.loads(workflow.result), **{"error": "paper is not available"}})
                workflow.status = FAILED
                workflow.save()
            old_path = paper.file_path
            if old_path:
                # delete old paper because user must have selected "replace" in this position
                _ = cdn_client.delete_paper(old_path)
            paper.file_path = file_path
            paper.save()

            workflow.stage = S_END
            workflow.status = COMPLETED
            workflow.save()

        elif work_type == PROCESS:
            pid = request.POST.get("pid")
            paper = Paper.objects.filter(id=pid, owner_id=uid).first()
            if not paper:
                return

            # in case of caching, re-query
            workflow = Workflow.objects.filter(id=wid).first()
            if not workflow or workflow.status == ABORTED:
                return
            workflow.stage = S_PROCESSING_0
            workflow.save()

            # Task 0: retrieve paper
            file_path = paper.file_path
            cdn_client = SakanaCDNClient()
            file_obj = cdn_client.request_for_paper(file_path)

            # in case of caching, re-query
            workflow = Workflow.objects.filter(id=wid).first()
            if not workflow or workflow.status == ABORTED:
                return
            workflow.stage = S_PROCESSING_1
            workflow.save()

            # Task 1: read and process paper
            tags = request.POST.getlist("tag-names")
            tags_dict = {}  # key: tag name, value: definition
            for t in tags:
                tag = Tag.objects.filter(name=t).first()
                tags_dict[t] = tag.definition
            llm_client = SimpleKeywordClient()
            matching_tags = llm_client.match_paper_on_tags(file_obj, tags)

            # in case of caching, re-query
            workflow = Workflow.objects.filter(id=wid).first()
            if not workflow or workflow.status == ABORTED:
                return
            workflow.stage = S_PROCESSING_2
            workflow.save()

            # Task 2: tag paper (add matching tags, remove non-matching)
            paper = Paper.objects.filter(id=pid, owner_id=uid).first()
            if not paper:
                return
            original_tags = [t.name for t in paper.tags.all()]
            added_tags = []
            removed_tags = []
            kept_tags = []
            for t in matching_tags:
                if t in original_tags:
                    kept_tags.append(t)
                else:
                    added_tags.append(t)
                tag = Tag.objects.filter(name=t).first()
                if tag:
                    paper.tags.add(tag)
            for t in tags:
                if t in original_tags and t not in matching_tags:
                    tag = Tag.objects.filter(name=t).first()
                    if tag:
                        paper.tags.remove(tag)
                    removed_tags.append(t)

            # in case of caching, re-query
            workflow = Workflow.objects.filter(id=wid).first()
            if not workflow or workflow.status == ABORTED:
                return
            workflow.stage = S_END
            workflow.status = COMPLETED
            workflow.result = json.dumps({**json.loads(workflow.result), **{"added_tags": added_tags,
                                                                            "removed_tags": removed_tags,
                                                                            "kept_tags": kept_tags}})
            workflow.save()

        else:  # illegal work type parameter
            return
    except Exception as e:
        workflow.result = json.dumps({**json.loads(workflow.result), **{"error": str(e)}})
        workflow.status = FAILED
        workflow.save()


def handle_create_workflow(request):
    uid = request.session.get("uid")
    pending_workflow_count = Workflow.objects.filter(status=PENDING, user_id=uid).count()
    if pending_workflow_count >= PENDING_WORKFLOWS_LIMIT:
        err_msg = f"You can't have more than {PENDING_WORKFLOWS_LIMIT} workflows running at the same time. " \
                  f"Upgrade to premium to lift the limit."
        return JsonResponse({"status": 1, "err_msg": err_msg})
    file_obj = request.FILES.get("paper")
    work_type = int(req_type) if (req_type := request.POST.get("type")).isnumeric() else -1
    instructions = ""  # in case the variable in workflow creation not defined for some reasons
    if work_type == UPLOAD:
        title = request.POST.get("title")
        if not (file_obj and title):
            err_msg = "Please select a paper to upload and give a title!"
            return JsonResponse({"status": 1, "err_msg": err_msg})
        replace = not not request.POST.get("replace")
        paper = Paper.objects.filter(title=title, owner_id=uid).first()
        if paper and not replace:
            err_msg = "You have uploaded the same paper, check replace if you want to replace it"
            return JsonResponse({"status": 1, "err_msg": err_msg})
        if not paper:
            paper = Paper(title=title, owner_id=uid)
            paper.save()
        pid = paper.id
        instructions = f"paper: {title}"
    elif work_type == PROCESS:
        pid = request.POST.get("pid")
        paper = Paper.objects.filter(id=pid).first()
        if not paper:
            err_msg = "The paper you want to process does not exist, please select again"
            return JsonResponse({"status": 1, "err_msg": err_msg})
        tags = request.POST.getlist("tag-names")
        for n in tags:
            tag = Tag.objects.filter(name=n).first()
            if not tag:
                err_msg = "Some tags selected do not exist!"
                return JsonResponse({"status": 1, "err_msg": err_msg})
        instructions = f'tags: {", ".join(tags)}'
    else:
        err_msg = "Illegal workflow creation"
        return JsonResponse({"status": 1, "err_msg": err_msg})

    # VERY IMPORTANT: file object might be closed after request complete, so we read all of it before sending response
    # Of course, this could take a long time, so on the web page we inform user of this
    file_obj = BytesIO(file_obj.read()) if file_obj else None

    name = request.POST.get("name")
    if not name:  # when name is an empty string
        name = "Untitled Workflow"

    # user cannot upload, process or upload_process at the same time
    workflow = Workflow.objects.filter(user_id=uid, paper_id=paper, work_type__in=INCOMPATIBLE_WORK_TYPE,
                                       status=PENDING).first()
    if workflow:
        err_msg = "You have a running workflow with the same paper. Abort it first or wait for it to complete"
        return JsonResponse({"status": 1, "err_msg": err_msg})

    workflow = Workflow(user_id=uid, paper_id=pid, name=name, work_type=work_type, instructions=instructions,
                        stage=S_START, status=PENDING)
    workflow.save()
    wid = workflow.id

    thread = threading.Thread(target=start_workflow_task, args=[request, wid, file_obj], daemon=True)
    thread.start()
    workflow.messages = f"Thread id {thread.ident}; "
    workflow.save()
    return JsonResponse({"status": 0, "wid": wid})


@login_required()
def get_workflow_status(request):
    wid = request.GET.get("wid")
    workflow = Workflow.objects.filter(id=wid).first()
    if not workflow:
        err_msg = "Something went wrong! Please refresh page or try again later"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    is_done = workflow.status in END_POLLING_STATUS
    return JsonResponse({"status": 0, "is_done": is_done})


@login_required()
def add_tags(request):
    uid = request.session.get("uid")
    pid = request.POST.get("pid")
    paper = Paper.objects.filter(id=pid, owner_id=uid).first()
    if not paper:
        err_msg = "Paper does not exist!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    tags = request.POST.get("tags", "")
    tags = [tag for t in tags.split(";") if (tag := t.strip()) != '']
    for t in tags:
        tag = Tag.objects.filter(name=t).first()
        if not tag:
            tag = Tag(name=t, adder_id=uid)
            tag.save()
        paper.tags.add(tag)
    return JsonResponse({"status": 0})


class WorkflowUserListView(ListView):
    model = SakanaUser  # in the url, we want uid as parameter, not pid
    paginate_by = 10
    template_name = "core/workflow_user_list.html"

    def get_queryset(self):
        uid = self.request.session.get("uid")
        # only shows unarchived workflows
        return Workflow.objects.filter(user_id=uid, is_archived=False)


@login_required()
def abort_workflow(request):
    uid = request.session.get("uid")
    wid = request.POST.get("wid")
    workflow = Workflow.objects.filter(id=wid, user_id=uid).first()
    if not workflow:
        err_msg = "Workflow does not exist!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    status = workflow.status
    if status == ABORTED:
        return JsonResponse({"status": 0})
    if status not in CAN_ABORT_STATUS:
        err_msg = f'You can not abort workflow with status "{status}"'
        return JsonResponse({"status": 1, "err_msg": err_msg})

    paper = workflow.paper
    # if workflow aborted before upload of new (otherwise there should be an old filepath) paper completed
    if not paper.file_path:
        workflow.paper.delete()
        alert_msg = "It seems that you are aborting a workflow while paper upload is not completed. " \
                    "This action deletes the workflow and you will now be redirected to homepage."
        return JsonResponse({"status": 1, "alert_msg": alert_msg})
    workflow.messages += "Manual abortion; "
    workflow.status = ABORTED
    workflow.save()
    return JsonResponse({"status": 0})


@login_required()
def add_tag_and_definition_page(request):
    return render(request, "core/tag_definition_add.html")


@login_required()
def add_tag_and_definition(request):
    tag_name = request.POST.get("name")
    if not tag_name:
        err_msg = "Please enter a tag name!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    tag_name = tag_name.replace(";", "").strip()
    uid = request.session.get("uid")
    tag = Tag.objects.filter(name=tag_name).first()
    definition = request.POST.get("definition")
    # if tag already exists
    if tag:
        if tag.adder_id != uid:  # adder is other user
            err_msg = f'Tag added by somebody else. Please contact "{tag.adder.auth_user.username}" via ' \
                      f'{tag.adder.auth_user.email}'
            return JsonResponse({"status": 1, "err_msg": err_msg})
        # adder is current user
        err_msg = "You have added the same tag, please go to update definition page"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    # else
    tag = Tag(name=tag_name, definition=definition, adder_id=uid)
    tag.save()
    return JsonResponse({"status": 0, "tag_name": tag_name})


@login_required()
def search_page(request):
    tags = Tag.objects.all()
    return render(request, "core/search.html", {"tags": list(tags)})


@login_required()
def search_result(request):
    uid = request.session.get("uid")
    partial_title = request.GET.get("title")
    owner = request.GET.get("owner")
    tags_contain = request.GET.getlist("tags-contain")
    tags_in = request.GET.getlist("tags-in")

    if tags_contain and tags_in:
        err_msg = 'Unfortunately it is impossible to search for both "Matches Tags" and "Has Tags"'
        return render(request, "core/search_result.html", {"err_msg": err_msg})

    if not owner:
        err_msg = "Please select a owner type to filter"
        return render(request, "core/search_result.html", {"err_msg": err_msg})

    # First filter tags_contain and tags_in
    if tags_contain:
        if "untagged;" in tags_contain:  # impossible for other tags to have a semicolon
            papers = Paper.objects.filter(tags__isnull=True)
        else:
            papers = Paper.objects.annotate(
                num_tags=Count('tags', filter=Q(tags__name__in=tags_contain))
            ).filter(num_tags=len(tags_contain))
    elif tags_in:  # impossible for other tags to have a semicolon
        papers = Paper.objects.filter(tags__name__in=tags_in)
        if "untagged;" in tags_in:
            papers |= Paper.objects.filter(tags__isnull=True)
        # papers = Paper.objects.filter( tags__name__in=["game theory", "Nash Equilibrium"]).exclude(owner_id=2)
    else:
        papers = Paper.objects.all()

    # Then filter title
    if partial_title:
        papers = papers.filter(title__icontains=partial_title)  # case insensitive

    # Lastly filter owner
    if owner == "me":
        papers = papers.filter(owner_id=uid)
    elif owner == "others":
        papers = papers.exclude(owner_id=uid)
    return render(request, "core/search_result.html", {"papers": papers})


class WorkflowUserArchivedListView(ListView):
    model = SakanaUser  # in the url, we want uid as parameter, not pid
    paginate_by = 10
    template_name = "core/workflow_user_archived_list.html"

    def get_queryset(self):
        uid = self.request.session.get("uid")
        # only shows unarchived workflows
        return Workflow.objects.filter(user_id=uid, is_archived=True)


@login_required()
def archive_workflow(request):
    uid = request.session.get("uid")
    wid = request.POST.get("wid")
    workflow = Workflow.objects.filter(id=wid, user_id=uid).first()
    if not workflow:
        err_msg = "Workflow does not exist!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    if workflow.is_archived:
        err_msg = "Can't archive an archived workflow!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    if (status := workflow.status) not in CAN_ARCHIVE_STATUS:
        err_msg = f"Can't archive if workflow status is {status}!"
        return JsonResponse({"status": 1, "err_msg": err_msg})

    workflow.is_archived = True
    workflow.save()
    return JsonResponse({"status": 0})


@login_required()
def restore_workflow(request):
    uid = request.session.get("uid")
    wid = request.POST.get("wid")
    workflow = Workflow.objects.filter(id=wid, user_id=uid).first()
    if not workflow:
        err_msg = "Workflow does not exist!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    if not workflow.is_archived:
        err_msg = "Can't restore an unarchived workflow!"
        return JsonResponse({"status": 1, "err_msg": err_msg})

    workflow.is_archived = False
    workflow.save()
    return JsonResponse({"status": 0})


@login_required()
def delete_paper(request):
    uid = request.session.get("uid")
    pid = request.POST.get("pid")
    paper = Paper.objects.filter(id=pid, owner_id=uid).first()
    if not paper:
        err_msg = "Paper does not exist!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    if not paper.file_path:  # could be deleting a paper before the upload finishes
        err_msg = "Invalid request, please contact the administrator!"
        return JsonResponse({"status": 1, "err_msg": err_msg})

    cdn_client = SakanaCDNClient()
    _ = cdn_client.delete_paper(paper.file_path)
    paper.delete()
    return JsonResponse({"status": 0})
