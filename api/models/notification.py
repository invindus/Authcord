import uuid

from django.db import models

from .author import Author


class Notification(models.Model):
    recipient = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="notifications"
    )
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=100)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
