import asyncio
import json
import threading

from asgiref.sync import sync_to_async
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.generic import DetailView, ListView
from django.contrib.auth.decorators import login_required

from .macros import *
from .models import Paper, Tag, SakanaUser, Workflow
from .cdn_utils import PseudoCDNClient
from .llm_utils import PseudoLLMClient


def home_page(request):
    uid = request.session.get("uid")
    # only display 10 most recent workflows on homepage
    workflows = Workflow.objects.filter(starter__uid=uid)[:10]
    return render(request, "core/index.html", {"workflows": workflows})


@login_required()
def upload_paper_page(request):
    return render(request, "core/paper_upload.html")


@login_required()
def process_paper_page(request):
    uid = request.session.get("uid")
    papers = Paper.objects.filter(owner_id=uid)
    return render(request, "core/paper_process.html", {"papers": papers})


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
        workflow = Workflow.objects.filter(wid=self.kwargs['pk']).first()
        if workflow:
            context["tags"] = json.loads(workflow.result).get("generated_tags", [])
            context["in_progress"] = IN_PROGRESS
            context["tags_ready"] = TAGS_READY
            context["can_abort_status"] = CAN_ABORT_STATUS
        return context


@sync_to_async
def async_get_uid(request):
    return request.session.get("uid")


async def _start_workflow_task(request, wid):
    workflow = await Workflow.objects.filter(wid=wid).afirst()
    if not workflow:
        return

    uid = await async_get_uid(request)
    file_obj = request.FILES.get("paper")
    title = request.POST.get("title")

    work_type = request.POST.get("type")
    if work_type == UPLOAD_AND_PROCESS:

        paper = await Paper.objects.filter(title=title, owner_id=uid).afirst()
        if not paper:
            return

        # in case of caching, re-query
        workflow = await Workflow.objects.filter(wid=wid).afirst()
        if not workflow or workflow.status == ABORTED:
            return
        workflow.stage = S_UPLOAD_AND_PROCESS
        await workflow.asave()
        # asynchronously execute CDN and LLM tasks
        cdn_client = PseudoCDNClient()
        llm_client = PseudoLLMClient()
        cdn_task = asyncio.create_task(cdn_client.store_paper(file_obj))
        llm_task = asyncio.create_task(llm_client.generate_tags_for_paper(file_obj))
        task_list = [cdn_task, llm_task]
        results = await asyncio.gather(*task_list)  # wait for tasks to complete and gather results
        file_path = results[0]  # CDN task result
        tags = results[1]  # LLM task result

        # in case of caching, re-query
        workflow = await Workflow.objects.filter(wid=wid).afirst()
        # if workflow is aborted or deleted (not allowed for users)
        if not workflow or workflow.status == ABORTED:
            _ = await cdn_client.delete_paper(file_path)  # delete new paper
            paper = await Paper.objects.filter(title=title, owner_id=uid).afirst()
            if not paper:  # if paper is deleted
                return
            if not paper.file_path:  # delete paper entry
                await paper.adelete()
            return
        # else
        paper = await Paper.objects.filter(title=title, owner_id=uid).afirst()
        if not paper:  # if paper is deleted or altered during normal workflow execution
            workflow.result = json.dumps({**json.loads(workflow.result), **{"error": "paper is not available"}})
            workflow.status = FAILED
            await workflow.asave()
        old_path = paper.file_path
        if old_path:
            # delete old paper because user must have selected "replace" in this position
            _ = await cdn_client.delete_paper(old_path)
        paper.file_path = file_path
        await paper.asave()

        result = json.loads(workflow.result)
        result = {**result, **{"generated_tags": tags}}
        workflow.result = json.dumps(result)
        workflow.stage = S_POST_PROCESS
        workflow.status = TAGS_READY
        await workflow.asave()


def start_workflow_task(request, wid):  # we need to pass a sync function to thread
    asyncio.run(_start_workflow_task(request, wid))


def handle_create_workflow(request):
    uid = request.session.get("uid")
    work_type = request.POST.get("type")
    if work_type == UPLOAD_AND_PROCESS or work_type == UPLOAD:
        file_obj = request.FILES.get("paper")
        title = request.POST.get("title")
        if not (file_obj and title):
            err_msg = "Please select a paper to upload and give a title!"
            return render(request, "core/paper_upload.html", {"err_msg": err_msg})
        replace = not not request.POST.get("replace")
        paper = Paper.objects.filter(title=title, owner_id=uid).first()
        if paper and not replace:
            err_msg = "You have uploaded the same paper, check replace if you want to replace it"
            return render(request, "core/paper_upload.html", {"err_msg": err_msg})
        if not paper:
            paper = Paper(title=title, owner_id=uid)
            paper.save()
        pid = paper.pid
    elif work_type == PROCESS:
        pid = request.POST.get("pid")
        paper = Paper.objects.filter(pid=pid).first()
        if not paper:
            err_msg = "The paper you want to process does not exist, please check again"
            return render(request, "core/paper_upload.html", {"err_msg": err_msg})
    else:
        err_msg = "Illegal workflow creation"
        return render(request, "core/paper_upload.html", {"err_msg": err_msg})

    name = request.POST.get("name")
    if not name:  # when name is an empty string
        name = "Untitled Workflow"

    # user cannot upload, process or upload_process at the same time
    workflow = Workflow.objects.filter(starter_id=uid, paper_id=paper, work_type__in=INCOMPATIBLE_WORK_TYPE,
                                       status=IN_PROGRESS).first()
    if workflow:
        err_msg = "You have a running workflow with the same paper. Abort it first or wait for it to complete"
        return render(request, "core/paper_upload.html", {"err_msg": err_msg})

    workflow = Workflow(starter_id=uid, paper_id=pid, name=name, work_type=work_type, stage=S_START, status=IN_PROGRESS)
    workflow.save()
    wid = workflow.wid

    thread = threading.Thread(target=start_workflow_task, args=[request, wid], daemon=True)
    thread.start()
    workflow.messages = f"Thread id {thread.ident}; "
    workflow.save()
    return redirect(f"/workflow/{wid}")


@login_required()
def get_workflow_status(request):
    wid = request.GET.get("wid")
    workflow = Workflow.objects.filter(wid=wid).first()
    if not workflow:
        err_msg = "Something went wrong! Please refresh page or try again later"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    is_done = workflow.status in END_POLLING_STATUS
    return JsonResponse({"status": 0, "is_done": is_done})


@login_required()
def add_tags(request):
    uid = request.session.get("uid")
    pid = request.POST.get("pid")
    paper = Paper.objects.filter(pid=pid, owner_id=uid).first()
    if not paper:
        err_msg = "Paper does not exist!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    tags = request.POST.get("tags", "")
    tags = [tag for t in tags.split(";") if (tag := t.strip()) != '']
    for t in tags:
        tag = Tag.objects.filter(name=t).first()
        if not tag:
            tag = Tag(name=t)
            tag.save()
        paper.tags.add(tag)
    return JsonResponse({"status": 0})


class WorkflowUserListView(ListView):
    model = SakanaUser  # in the url, we want uid as parameter, not pid
    paginate_by = 10
    template_name = "core/workflow_user_list.html"

    def get_queryset(self):
        uid = self.request.session.get("uid")
        return Workflow.objects.filter(starter_id=uid)


@login_required()
def workflow_add_tags(request):
    uid = request.session.get("uid")
    wid = request.POST.get("wid")
    workflow = Workflow.objects.filter(wid=wid, starter_id=uid).first()
    if not workflow or workflow.status == ABORTED:
        err_msg = "Workflow is not available for operations!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    paper = workflow.paper

    tags = request.POST.get("tags", "")
    tags = [tag for t in tags.split(";") if (tag := t.strip()) != '']
    for t in tags:
        tag = Tag.objects.filter(name=t).first()
        if not tag:
            tag = Tag(name=t)
            tag.save()
        paper.tags.add(tag)

    # in case of caching, re-query
    workflow = Workflow.objects.filter(wid=wid).first()
    if workflow.status == ABORTED:
        err_msg = "Workflow is already aborted!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    workflow.stage = S_FINISH
    workflow.status = COMPLETE
    workflow.save()

    return JsonResponse({"status": 0})


@login_required()
def abort_workflow(request):
    uid = request.session.get("uid")
    wid = request.POST.get("wid")
    workflow = Workflow.objects.filter(wid=wid, starter_id=uid).first()
    if not workflow:
        err_msg = "Workflow does not exist!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    status = workflow.status
    if status == ABORTED:
        return JsonResponse({"status": 0})
    if status not in CAN_ABORT_STATUS:
        err_msg = f'You can not abort workflow with status "{status}"'
        return JsonResponse({"status": 1, "err_msg": err_msg})

    messages = workflow.messages
    messages += "Manual abortion; "
    workflow.messages = messages
    workflow.status = ABORTED
    workflow.save()
    return JsonResponse({"status": 0})
