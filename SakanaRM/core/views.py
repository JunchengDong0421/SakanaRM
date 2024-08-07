import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from os import name as os_name

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import DetailView, ListView
from zoneinfo import ZoneInfo  # Python 3.9 or later only

from .config import PENDING_WORKFLOWS_LIMIT
from .storage_utils import SakanaStorageClient
from .llm_utils import GPTClient, SimpleKeywordClient
from .models import Paper, Tag, SakanaUser, Workflow

# incompatible work types
INCOMPATIBLE_WORK_TYPE = (Workflow.WorkTypeChoices.UPLOAD, Workflow.WorkTypeChoices.PROCESS)
# statuses - end polling
END_POLLING_STATUS = (Workflow.StatusChoices.COMPLETED, Workflow.StatusChoices.FAILED, Workflow.StatusChoices.ABORTED)
# statuses - can abort
CAN_ABORT_STATUS = (Workflow.StatusChoices.PENDING,)
# statuses - can archive
CAN_ARCHIVE_STATUS = (Workflow.StatusChoices.COMPLETED, Workflow.StatusChoices.FAILED, Workflow.StatusChoices.ABORTED)

executor = ThreadPoolExecutor()

logger = logging.getLogger(__name__)


def home_page(request):
    uid = request.session.get("uid")
    # only display 10 most recent workflows on homepage
    workflows = Workflow.objects.filter(user_id=uid, is_archived=False)[:10]
    return render(request, "core/index.html", {"workflows": workflows})


@login_required()
def upload_paper_page(request):
    return render(request, "core/paper_upload.html", {"UPLOAD": Workflow.WorkTypeChoices.UPLOAD})


@login_required()
def process_paper_page(request):
    uid = request.session.get("uid")
    papers = Paper.objects.filter(owner_id=uid)
    tags = Tag.objects.all()
    return render(request, "core/paper_process.html",
                  {"papers": papers, "tags": tags, "PROCESS": Workflow.WorkTypeChoices.PROCESS})


class PaperDetailView(DetailView):
    model = Paper

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tags = Tag.objects.all()
        context["tags"] = tags
        return context


class PaperUserListView(LoginRequiredMixin, ListView):
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
            context["pending"] = Workflow.StatusChoices.PENDING
            context["completed"] = Workflow.StatusChoices.COMPLETED
            context["failed"] = Workflow.StatusChoices.FAILED
            context["upload"] = Workflow.WorkTypeChoices.UPLOAD
            context["process"] = Workflow.WorkTypeChoices.PROCESS
            context["can_abort_status"] = CAN_ABORT_STATUS
        return context


def start_workflow_task(request, wid, file_obj):
    workflow = Workflow.objects.filter(id=wid).first()
    if not workflow or workflow.status == Workflow.StatusChoices.ABORTED:
        return
    try:
        uid = request.session.get('uid')
        title = request.POST.get("title")

        work_type = int(request.POST.get("type"))
        if work_type == Workflow.WorkTypeChoices.UPLOAD:
            workflow.stage = Workflow.StageChoices.S_UPLOADING
            workflow.save()

            storage_client = SakanaStorageClient()
            replace = not not request.POST.get("replace")
            if not replace:  # upload new paper
                file_path = storage_client.store_paper(file_obj)
            else:  # replace existing paper
                paper = workflow.paper
                if not paper:
                    return
                filepath = paper.file_path
                file_path = storage_client.replace_paper(filepath, file_obj)

            # in case of caching, re-query
            workflow = Workflow.objects.filter(id=wid).first()
            # if workflow is aborted or deleted (not allowed for users)
            if not workflow or workflow.status == Workflow.StatusChoices.ABORTED:
                _ = storage_client.delete_paper(file_path)  # delete new paper
                paper = Paper.objects.filter(title=title, owner_id=uid).first()
                if not paper:  # if paper is deleted
                    return
                if not paper.file_path:  # delete paper entry
                    paper.delete()
                return
            # otherwise continue
            if not replace:  # upload new paper
                paper = Paper(title=title, owner_id=uid, file_path=file_path)
                paper.save()
                workflow.paper = paper
                workflow.save()
            else:  # replace existing paper
                paper = workflow.paper
                if not paper:
                    return
                paper.file_path = file_path
                paper.save()

            workflow.stage = Workflow.StageChoices.S_END
            workflow.status = Workflow.StatusChoices.COMPLETED
            workflow.save()

        elif work_type == Workflow.WorkTypeChoices.PROCESS:
            paper = workflow.paper
            if not paper:
                return

            # in case of caching, re-query
            workflow = Workflow.objects.filter(id=wid).first()
            if not workflow or workflow.status == Workflow.StatusChoices.ABORTED:
                return
            workflow.stage = Workflow.StageChoices.S_PROCESSING_0
            workflow.save()

            # Task 0: retrieve paper
            file_path = paper.file_path
            storage_client = SakanaStorageClient()
            file_obj = storage_client.request_for_paper(file_path)

            # in case of caching, re-query
            workflow = Workflow.objects.filter(id=wid).first()
            if not workflow or workflow.status == Workflow.StatusChoices.ABORTED:
                return
            workflow.stage = Workflow.StageChoices.S_PROCESSING_1
            workflow.save()

            # Task 1: read and process paper
            tags = request.POST.getlist("tag-names")
            tags_dict = {}  # key: tag name, value: definition
            for t in tags:
                tag = Tag.objects.filter(name=t).first()
                tags_dict[t] = tag.definition
            llm_client = GPTClient()
            matching_tags = llm_client.match_paper_on_tags(file_obj, tags_dict)

            # in case of caching, re-query
            workflow = Workflow.objects.filter(id=wid).first()
            if not workflow or workflow.status == Workflow.StatusChoices.ABORTED:
                return
            workflow.stage = Workflow.StageChoices.S_PROCESSING_2
            workflow.save()

            # Task 2: tag paper (add matching tags, remove non-matching)
            paper = workflow.paper
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
            if not workflow or workflow.status == Workflow.StatusChoices.ABORTED:
                return
            workflow.stage = Workflow.StageChoices.S_END
            workflow.status = Workflow.StatusChoices.COMPLETED
            workflow.result = json.dumps(json.loads(workflow.result) | {"added_tags": added_tags,
                                                                        "removed_tags": removed_tags,
                                                                        "kept_tags": kept_tags})
            workflow.save()

        else:  # illegal work type parameter
            return
    except Exception as e:
        logger.error(repr(e))
        workflow.status = Workflow.StatusChoices.FAILED
        workflow.result = json.dumps(json.loads(workflow.result) | {"error": str(e)})
        workflow.save()


@login_required()
def handle_create_workflow(request):
    uid = request.session.get("uid")
    # check pending count
    pending_workflow_count = Workflow.objects.filter(status=Workflow.StatusChoices.PENDING, user_id=uid).count()
    if pending_workflow_count >= PENDING_WORKFLOWS_LIMIT:
        err_msg = f"You can't have more than {PENDING_WORKFLOWS_LIMIT} workflows running at the same time. "
        return JsonResponse({"status": 1, "err_msg": err_msg})
    # check name
    name = request.POST.get("name")
    if not name:  # when name is an empty string
        name = "Untitled Workflow"
    elif len(name) > (max_length := 100):  # if a name is provided and length exceeds max_length
        err_msg = f"Workflow name exceeds maximum length of {max_length} characters!"
        return JsonResponse({"status": 1, "err_msg": err_msg})

    file_obj = request.FILES.get("paper")
    work_type = request.POST.get("type")
    if not work_type:
        err_msg = "Invalid request!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    try:
        work_type = int(work_type)
    except ValueError:
        err_msg = "Illegal request parameter, please contact the administrator for help!"
        return JsonResponse({"status": 1, "err_msg": err_msg})

    if work_type == Workflow.WorkTypeChoices.UPLOAD:
        title = request.POST.get("title")
        if not (file_obj and title):
            err_msg = "Please select a paper to upload and give a title!"
            return JsonResponse({"status": 1, "err_msg": err_msg})
        replace = not not request.POST.get("replace")
        paper = Paper.objects.filter(title=title, owner_id=uid).first()
        if paper:  # replace existing paper
            if not replace:
                err_msg = "You have uploaded the same paper, check replace if you want to replace it"
                return JsonResponse({"status": 1, "err_msg": err_msg})
            pid = paper.id
            # user cannot upload and process the same paper at the same time
            workflow = Workflow.objects.filter(user_id=uid, paper_id=pid, work_type__in=INCOMPATIBLE_WORK_TYPE,
                                               status=Workflow.StatusChoices.PENDING).first()
            if workflow:
                err_msg = "You have a running workflow with the same paper. Abort it first or wait for it to complete"
                return JsonResponse({"status": 1, "err_msg": err_msg})
            instructions = f"paper (to replace): {title}"
            workflow = Workflow(user_id=uid, paper_id=pid, name=name, work_type=work_type, instructions=instructions,
                                stage=Workflow.StageChoices.S_START, status=Workflow.StatusChoices.PENDING)
        else:  # upload new paper
            instructions = f"paper: {title}"
            workflow = Workflow(user_id=uid, name=name, work_type=work_type, instructions=instructions,
                                stage=Workflow.StageChoices.S_START, status=Workflow.StatusChoices.PENDING)
    elif work_type == Workflow.WorkTypeChoices.PROCESS:
        pid = request.POST.get("pid")
        if not pid:
            err_msg = "Invalid request!"
            return JsonResponse({"status": 1, "err_msg": err_msg})
        try:
            pid = int(pid)
        except ValueError:
            err_msg = "Illegal request parameter, please contact the administrator for help!"
            return JsonResponse({"status": 1, "err_msg": err_msg})
        # user cannot upload and process the same paper at the same time
        workflow = Workflow.objects.filter(user_id=uid, paper_id=pid, work_type__in=INCOMPATIBLE_WORK_TYPE,
                                           status=Workflow.StatusChoices.PENDING).first()
        if workflow:
            err_msg = "You have a running workflow with the same paper. Abort it first or wait for it to complete"
            return JsonResponse({"status": 1, "err_msg": err_msg})
        paper = Paper.objects.filter(id=pid, owner_id=uid).first()
        if not paper:
            err_msg = "The paper you want to process does not exist or you do not have access to it, please re-select"
            return JsonResponse({"status": 1, "err_msg": err_msg})
        tags = request.POST.getlist("tag-names")
        if not tags:
            err_msg = "Please select some tags to process!"
            return JsonResponse({"status": 1, "err_msg": err_msg})
        for n in tags:
            tag = Tag.objects.filter(name=n).first()
            if not tag:
                err_msg = "Some selected tags do not exist!"
                return JsonResponse({"status": 1, "err_msg": err_msg})
        instructions = f'tags: {", ".join(tags)}'
        workflow = Workflow(user_id=uid, paper_id=pid, name=name, work_type=work_type, instructions=instructions,
                            stage=Workflow.StageChoices.S_START, status=Workflow.StatusChoices.PENDING)
    else:
        err_msg = "Illegal workflow creation!"
        return JsonResponse({"status": 1, "err_msg": err_msg})

    # VERY IMPORTANT: file object might be closed after request complete, so we read all of it before sending response
    # Of course, this could take a long time, so on the web page we inform user of this
    file_obj = BytesIO(file_obj.read()) if file_obj else None

    workflow.save()
    wid = workflow.id

    executor.submit(start_workflow_task, request, wid, file_obj)

    return JsonResponse({"status": 0, "wid": wid})


@login_required()
def get_workflow_status(request):
    wid = request.GET.get("wid")
    if not wid:
        err_msg = "Invalid request!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    try:
        wid = int(wid)
    except ValueError:
        err_msg = "Illegal request parameter, please contact the administrator for help!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    workflow = Workflow.objects.filter(id=wid).first()
    if not workflow:
        err_msg = "Something went wrong! Please refresh page or try again later"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    is_done = workflow.status in END_POLLING_STATUS
    return JsonResponse({"status": 0, "is_done": is_done})


class WorkflowUserListView(LoginRequiredMixin, ListView):
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
    if not wid:
        err_msg = "Invalid request!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    try:
        wid = int(wid)
    except ValueError:
        err_msg = "Illegal request parameter, please contact the administrator for help!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    workflow = Workflow.objects.filter(id=wid, user_id=uid).first()
    if not workflow:
        err_msg = "Workflow does not exist or you do not have access to it!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    status = workflow.status
    if status == Workflow.StatusChoices.ABORTED:
        return JsonResponse({"status": 0})
    if status not in CAN_ABORT_STATUS:
        err_msg = f'You can not abort workflow with status "{status}"'
        return JsonResponse({"status": 1, "err_msg": err_msg})
    # in case of obscure bugs or malicious requests
    if workflow.paper and not (paper := workflow.paper).file_path:
        paper.delete()
        alert_msg = "Something went wrong! The workflow will be deleted now and you will be redirected to homepage. " \
                    "Please contact the administrator for help."
        return JsonResponse({"status": 1, "alert_msg": alert_msg})
    workflow.messages += "Manual abortion; "
    workflow.status = Workflow.StatusChoices.ABORTED
    workflow.save()
    return JsonResponse({"status": 0})


@login_required()
def add_tag_and_definition_page(request):
    return render(request, "core/tag_definition_add.html")


@login_required()
def add_tag_and_definition(request):
    tag_name = request.POST.get("name")
    if not tag_name or not (processed_name := tag_name.replace(";", "").strip()):
        err_msg = "Please enter a valid tag name!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    if len(tag_name) > (max_length := 100):
        err_msg = f"Tag name exceeds maximum length of {max_length} characters!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    uid = request.session.get("uid")
    tag = Tag.objects.filter(name=processed_name).first()
    definition = request.POST.get("definition", "")  # allow for empty definition
    # if tag already exists
    if tag:
        if tag.adder_id != uid:  # adder is other user
            err_msg = f'Tag added by somebody else. Please contact "{tag.adder.display_name}" via ' \
                      f'{tag.adder.auth_user.email}.'
            return JsonResponse({"status": 1, "err_msg": err_msg})
        # adder is current user
        err_msg = "You have added the same tag!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    # else
    tag = Tag(name=processed_name, definition=definition, adder_id=uid)
    tag.save()
    return JsonResponse({"status": 0, "tag_name": processed_name})


class WorkflowUserArchivedListView(LoginRequiredMixin, ListView):
    model = SakanaUser  # in the url, we want uid as parameter, not pid
    paginate_by = 10
    template_name = "core/workflow_user_archived_list.html"

    def get_queryset(self):
        uid = self.request.session.get("uid")
        return Workflow.objects.filter(user_id=uid, is_archived=True)


@login_required()
def archive_workflow(request):
    uid = request.session.get("uid")
    wid = request.POST.get("wid")
    if not wid:
        err_msg = "Invalid request!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    try:
        wid = int(wid)
    except ValueError:
        err_msg = "Illegal request parameter, please contact the administrator for help!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    workflow = Workflow.objects.filter(id=wid, user_id=uid).first()
    if not workflow:
        err_msg = "Workflow does not exist or you do not have access to it!"
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
    if not wid:
        err_msg = "Invalid request!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    try:
        wid = int(wid)
    except ValueError:
        err_msg = "Illegal request parameter, please contact the administrator for help!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    workflow = Workflow.objects.filter(id=wid, user_id=uid).first()
    if not workflow:
        err_msg = "Workflow does not exist or you do not have access to it!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    if not workflow.is_archived:
        err_msg = "Can't restore an unarchived workflow!"
        return JsonResponse({"status": 1, "err_msg": err_msg})

    workflow.is_archived = False
    workflow.save()
    return JsonResponse({"status": 0})


@login_required()
def rename_workflow(request):
    uid = request.session.get("uid")
    wid = request.POST.get("wid")
    if not wid:
        err_msg = "Invalid request!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    try:
        wid = int(wid)
    except ValueError:
        err_msg = "Illegal request parameter, please contact the administrator for help!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    workflow = Workflow.objects.filter(id=wid, user_id=uid).first()
    if not workflow:
        err_msg = "Workflow does not exist or you do not have access to it!"
        return JsonResponse({"status": 1, "err_msg": err_msg})

    new_name = request.POST.get("name")
    workflow.name = new_name
    workflow.save()
    return JsonResponse({"status": 0})


@login_required()
def delete_paper(request):
    uid = request.session.get("uid")
    pid = request.POST.get("pid")
    if not pid:
        err_msg = "Invalid request!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    try:
        pid = int(pid)
    except ValueError:
        err_msg = "Illegal request parameter, please contact the administrator for help!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    paper = Paper.objects.filter(id=pid, owner_id=uid).first()
    if not paper:
        err_msg = "Paper does not exist or you do not have access to it!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    if paper.workflow_set.filter(
            status=Workflow.StatusChoices.PENDING).count() > 0:  # if paper still being used by some running workflows
        err_msg = "Cannot delete paper while a workflow associated with it is running!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    if not paper.file_path:  # in case of some obscure bugs or malicious requests
        err_msg = "Illegal request, please contact the administrator for help!"
        return JsonResponse({"status": 1, "err_msg": err_msg})

    try:
        storage_client = SakanaStorageClient()
        _ = storage_client.delete_paper(paper.file_path)
        paper.delete()
        return JsonResponse({"status": 0})
    except Exception as e:
        logger.error(repr(e))
        return JsonResponse({"status": 1, "err_msg": str(e)})


@login_required()
def update_tag_and_definition_page(request):
    uid = request.session.get("uid")
    tags = Tag.objects.filter(adder_id=uid)
    tag_name = request.GET.get("tagname")
    if not tag_name:
        selected_tid = -1
    else:
        selected_tag = tags.filter(name=tag_name).first()
        selected_tid = selected_tag.id if selected_tag else -1
    return render(request, "core/tag_definition_update.html", {"tags": tags, "s_tid": selected_tid})


@login_required()
def update_tag_and_definition(request):
    uid = request.session.get("uid")
    tid = request.POST.get("tid")
    if not tid:
        err_msg = "Invalid request!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    try:
        tid = int(tid)
    except ValueError:
        err_msg = "Illegal request parameter, please contact the administrator for help!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    tag = Tag.objects.filter(id=tid, adder_id=uid).first()
    if not tag:
        err_msg = "Tag does not exist or you do not have access to it!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    definition = request.POST.get("definition")
    tag.definition = definition
    tag.save()
    return JsonResponse({"status": 0, "tag_name": tag.name, "tag_def": tag.definition})


@login_required()
def paper_add_tags(request):
    uid = request.session.get("uid")
    pid = request.POST.get("pid")
    if not pid:
        err_msg = "Invalid request!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    try:
        pid = int(pid)
    except ValueError:
        err_msg = "Illegal request parameter, please contact the administrator for help!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    paper = Paper.objects.filter(id=pid, owner_id=uid).first()
    if not paper:
        err_msg = "Paper does not exist or you do not have access to it!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    # cannot add tags while paper is being uploaded or new upload failed
    # also in case of some obscure bugs or malicious requests
    if not paper.file_path:
        err_msg = "Illegal request, please contact the administrator for help!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    tag_ids = request.POST.getlist("tag-ids")
    if not tag_ids:
        err_msg = "Please select at least one tag to add!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    for tid in tag_ids:
        try:
            tid = int(tid)
        except ValueError:
            err_msg = "Illegal request parameter, please contact the administrator for help!"
            return JsonResponse({"status": 1, "err_msg": err_msg})
        tag = Tag.objects.filter(id=tid).first()  # allow for adding others' tags
        if not tag:
            err_msg = "Tag does not exist！"
            return JsonResponse({"status": 1, "err_msg": err_msg})
        paper.tags.add(tag)
    return JsonResponse({"status": 0})


@login_required()
def paper_remove_tags(request):
    uid = request.session.get("uid")
    pid = request.POST.get("pid")
    if not pid:
        err_msg = "Invalid request!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    try:
        pid = int(pid)
    except ValueError:
        err_msg = "Illegal request parameter, please contact the administrator for help!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    paper = Paper.objects.filter(id=pid, owner_id=uid).first()
    if not paper:
        err_msg = "Paper does not exist or you do not have access to it!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    # cannot remove tags while paper is being uploaded or new upload failed
    # also in case of some obscure bugs or malicious requests
    if not paper.file_path:
        err_msg = "Illegal request, please contact the administrator for help!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    tag_ids = request.POST.getlist("tag-ids")
    if not tag_ids:
        err_msg = "Please select at least one tag to remove!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    for tid in tag_ids:
        try:
            tid = int(tid)
        except ValueError:
            err_msg = "Illegal request parameter, please contact the administrator for help!"
            return JsonResponse({"status": 1, "err_msg": err_msg})
        tag = Tag.objects.filter(id=tid).first()
        if not tag:
            err_msg = "Tag does not exist！"
            return JsonResponse({"status": 1, "err_msg": err_msg})
        paper.tags.remove(tag)
    return JsonResponse({"status": 0})


def search_page(request):
    tags = Tag.objects.all()
    papers = Paper.objects.all()
    return render(request, "core/search.html", {"tags": tags, "papers": papers})


def search_result(request):
    uid = request.session.get("uid")
    partial_title = request.POST.get("title")
    owner = request.POST.get("owner")
    match_type = request.POST.get("match")
    tags = request.POST.getlist("tags")  # list of ids of tags, -1 if untagged

    legal_owners = ("anyone", "me", "others")
    legal_match_types = ("inclusive", "union")
    if owner not in legal_owners:
        err_msg = "Illegal request parameter, please contact the administrator for help!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    if not uid and owner != "anyone":
        err_msg = "Please log in first!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    if tags:
        if match_type not in legal_match_types:
            err_msg = "Please select a valid match type, or contact the administrator for help!"
            return JsonResponse({"status": 1, "err_msg": err_msg})
        for tid in tags:
            try:
                tid = int(tid)
            except ValueError:
                err_msg = "Illegal request parameter, please contact the administrator for help!"
                return JsonResponse({"status": 1, "err_msg": err_msg})
            if tid != -1:  # don't check for untagged
                tag = Tag.objects.filter(id=tid).count()
                if not tag:
                    err_msg = "Some selected tags do not exist!"
                    return JsonResponse({"status": 1, "err_msg": err_msg})

    # First get all papers
    papers = Paper.objects.all()

    # Then filter tags and match type
    if tags:
        if match_type == "inclusive":
            papers = papers.annotate(
                num_tags=Count('tags', filter=Q(tags__id__in=tags))
            ).filter(num_tags=len(tags) if "-1" not in tags else len(tags) - 1)
        elif match_type == "union":
            papers = papers.filter(tags__id__in=tags)  # exclude papers without tags
            if "-1" in tags:
                papers |= Paper.objects.filter(tags__isnull=True)  # add untagged papers back, filter all paper objects
            papers = papers.distinct()

    # Next filter owner
    if uid:
        if owner == "me":
            papers = papers.filter(owner_id=uid)
        elif owner == "others":
            papers = papers.exclude(owner_id=uid)

    # Finally filter title
    if partial_title:
        papers = papers.filter(title__icontains=partial_title)  # case insensitive

    # Different platforms (registered as: 'posix', 'nt' or 'java') use different flags to remove zero padding
    format_option = '%B %-d, %-Y, %-I:%M %p' if os_name == "posix" else '%B %#d, %#Y, %#I:%M %p' if os_name == "nt" \
        else '%B %d, %Y, %I:%M %p'
    # Pass and process columns data as JSON serializable objects
    papers = [
        {
            "id": p.id,
            "title": p.title,
            "tags": ", ".join(list(p.tags.all().values_list('name', flat=True))),
            "owner_name": p.owner.display_name,
            "last_modified": p.last_modified.astimezone(ZoneInfo(settings.TIME_ZONE)).strftime(format_option)
            .replace('PM', 'p.m.').replace('AM', 'a.m.')
        } for p in papers
    ]
    return JsonResponse({"status": 0, "papers": papers})


class TagUserListView(LoginRequiredMixin, ListView):
    model = SakanaUser
    paginate_by = 20
    template_name = "core/tag_user_list.html"

    def get_queryset(self):
        uid = self.request.session.get("uid")
        return Tag.objects.filter(adder_id=uid).annotate(paper_count=Count("paper")).order_by("name")


@login_required()
def delete_tag_and_definition(request):  # delete tag instance, for uniformity we add 'and_definition' to function name
    uid = request.session.get("uid")
    tid = request.POST.get("tid")
    if not tid:
        err_msg = "Invalid request!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    tag = Tag.objects.filter(id=tid, adder_id=uid).first()
    if not tag:
        err_msg = "Tag does not exist or you do not have access to it!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    tag.delete()
    return JsonResponse({"status": 0})


def about_page(request):
    return render(request, "core/about.html")


def tutorial_page(request):
    return render(request, "core/tutorial.html")


def custom_404_view(request, exception):
    return render(request, "core/404.html")


def custom_500_view(request):
    return render(request, "core/500.html")
