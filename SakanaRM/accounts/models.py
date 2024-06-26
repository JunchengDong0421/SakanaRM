from django.contrib.auth.models import User
from django.db import models


class SakanaUser(models.Model):
    # Extended User model for the application

    id = models.BigAutoField(primary_key=True)
    auth_user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"<SakanaUser uid={self.id} username={self.auth_user.get_username()}>"
