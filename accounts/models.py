from django.db import models
from django.contrib.auth.models import User


class SakanaUser(models.Model):
    # Extended User model for the application

    uid = models.BigAutoField(primary_key=True)
    auth_user = models.OneToOneField(User, on_delete=models.CASCADE)
