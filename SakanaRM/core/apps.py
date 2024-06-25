import json

from django.apps import AppConfig
from django.db.models import Q


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        # Must import models inside function, otherwise AppRegistryNotReady exception
        from .models import Paper, Workflow
        # Set status of all pending workflows to failed
        _ = Workflow.objects.filter(status=Workflow.StatusChoices.PENDING) \
            .update(status=Workflow.StatusChoices.FAILED,
                    result=json.dumps({"error": "Server restart, workflow progress is lost"})
                    )
        # Delete all papers with an empty filepath
        _, _ = Paper.objects.filter(Q(file_path__isnull=True) | Q(file_path="")).delete()
