from django.db import models
from django.contrib.auth.models import User

from accounts.models import SakanaUser


class Tag(models.Model):
    class Meta:
        ordering = ["name"]  # default ordering is by tag name

    tid = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    definition = models.TextField()

    # Will automatically be filled in once instance is instantiated
    created_at = models.DateTimeField(auto_now_add=True)
    # Will automatically be updated once save() is called on an instance
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<Tag tid={self.tid} name={self.name}>"


class Paper(models.Model):
    class Meta:
        ordering = ["title"]  # default ordering is by paper title

    pid = models.BigAutoField(primary_key=True)
    title = models.TextField()
    file_path = models.TextField()
    tags = models.ManyToManyField(Tag)  # ManyToMany relation to Tag
    owner = models.ForeignKey(SakanaUser, on_delete=models.CASCADE)  # ManyToOne relation to SakanaUser

    # Will automatically be filled in once instance is instantiated
    created_at = models.DateTimeField(auto_now_add=True)
    # Will automatically be updated once save() is called on an instance
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<Tag tid={self.pid} title={self.title}>"


class Workflow(models.Model):
    class Meta:
        ordering = ["-last_updated"]

    wid = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, default="Untitled Workflow")
    starter = models.ForeignKey(SakanaUser, on_delete=models.CASCADE)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)  # delete all associating workflows when deleting a paper
    work_type = models.CharField(max_length=50)
    instructions = models.TextField()
    stage = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    messages = models.TextField()
    result = models.TextField(default="{}")

    started_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"<Workflow wid={self.wid} name={self.name} stage={self.stage} status={self.status}>"
