from django.db import models
from django.contrib.auth.models import User

from accounts.models import SakanaUser


# Create your models here.
class Tag(models.Model):
    class Meta:
        ordering = ["name"]  # default ordering is by tag name

    tid = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField()

    # Will automatically be filled in once instance is instantiated
    created_at = models.DateTimeField(auto_now_add=True)
    # Will automatically be updated once save() is called on an instance
    last_modified = models.DateTimeField(auto_now=True)


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
