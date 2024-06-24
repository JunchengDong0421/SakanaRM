from django.contrib.auth.models import User
from django.db import models

from accounts.models import SakanaUser


class Tag(models.Model):
    class Meta:
        ordering = ["name"]  # default ordering is by tag name

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    definition = models.TextField()
    adder = models.ForeignKey(SakanaUser, on_delete=models.CASCADE)  # ManyToOne relation to SakanaUser

    # Will automatically be filled in once instance is instantiated
    created_at = models.DateTimeField(auto_now_add=True)
    # Will automatically be updated once save() is called on an instance
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<Tag tid={self.id} name={self.name}>"


class Paper(models.Model):
    class Meta:
        ordering = ["title"]  # default ordering is by paper title

    id = models.BigAutoField(primary_key=True)
    title = models.TextField()
    file_path = models.TextField()
    tags = models.ManyToManyField(Tag)  # ManyToMany relation to Tag
    owner = models.ForeignKey(SakanaUser, on_delete=models.CASCADE)  # ManyToOne relation to SakanaUser

    # Will automatically be filled in once instance is instantiated
    created_at = models.DateTimeField(auto_now_add=True)
    # Will automatically be updated once save() is called on an instance
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<Paper pid={self.id} title={self.title}>"


class Workflow(models.Model):
    class Meta:
        ordering = ["-last_updated"]

    class WorkTypeChoices(models.IntegerChoices):
        UPLOAD = 0, "upload"
        PROCESS = 1, "process"
        OTHER = 2, "other"

    class StageChoices(models.IntegerChoices):
        S_START = 0, "start"
        S_UPLOADING = 1, "uploading"
        S_PROCESSING_0 = 2, "retrieving"
        S_PROCESSING_1 = 3, "processing"
        S_PROCESSING_2 = 4, "tagging"
        S_END = 5, "end"

    class StatusChoices(models.IntegerChoices):
        PENDING = 0, "pending"
        COMPLETED = 1, "completed"
        FAILED = 2, "failed"
        ABORTED = 3, "aborted"

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, default="Untitled Workflow")
    user = models.ForeignKey(SakanaUser, on_delete=models.CASCADE)
    # delete all associating workflows when deleting a paper, can be nullable
    paper = models.ForeignKey(Paper, null=True, on_delete=models.CASCADE)
    work_type = models.IntegerField(choices=WorkTypeChoices.choices, default=WorkTypeChoices.OTHER)
    instructions = models.TextField()
    stage = models.IntegerField(choices=StageChoices.choices, default=StageChoices.S_START)
    status = models.IntegerField(choices=StatusChoices.choices, default=StatusChoices.PENDING)
    messages = models.TextField()
    result = models.TextField(default="{}")

    started_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"<Workflow wid={self.id} name={self.name} stage={self.get_stage_display()} " \
               f"status={self.get_status_display()}>"
