from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_page, name="index"),
    path("paper/<int:pk>", views.PaperDetailView.as_view(), name="paper-detail"),
    path("user/<int:pk>/papers", views.PaperUserListView.as_view(), name="my-papers"),

    path("paper/upload", views.upload_paper_page, name="upload-paper-page"),
    path("paper/process", views.process_paper_page, name="process-paper-page"),
    path("workflow/<int:pk>", views.WorkflowDetailView.as_view(), name="workflow-detail"),
    path("api/workflow/create", views.handle_create_workflow, name="create-workflow"),
    path("user/<int:pk>/workflows", views.WorkflowUserListView.as_view(), name="my-workflows"),
    path("user/<int:pk>/archived/workflows", views.WorkflowUserArchivedListView.as_view(),
         name="my-archived-workflows"),
    path("tag/add", views.add_tag_and_definition_page, name="add-tag-definition-page"),

    path("api/paper/addtags", views.add_tags, name="add-tags"),
    path("api/paper/delete", views.delete_paper, name="delete-paper"),
    path("api/workflow/status", views.get_workflow_status, name="workflow-status"),
    path("api/workflow/addtags", views.workflow_add_tags, name="workflow-add-tags"),
    path("api/workflow/abort", views.abort_workflow, name="abort-workflow"),
    path("api/workflow/archive", views.archive_workflow, name="archive-workflow"),
    path("api/workflow/restore", views.restore_workflow, name="restore-workflow"),
    path("api/tag/add", views.add_tag_and_definition, name="add-tag-definition"),

    path("search", views.search_page, name="search-page"),
    path("search/all", views.search_result, name="search-result")
]
