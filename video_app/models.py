from django.db import models
import uuid
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User  # Use the default User model


class Video(models.Model):
    file = models.FileField(upload_to='videos/')
    size = models.BigIntegerField()  # File size in bytes
    duration = models.FloatField()  # Duration in seconds
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')


class SharedLink(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="shared_links")
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    expiry_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.expiry_time
    