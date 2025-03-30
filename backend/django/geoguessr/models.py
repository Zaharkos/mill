import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now, timedelta


class UserRole(models.TextChoices):
    ADMIN = "admin", "Administrator"
    PROVIDER = "provider", "Photo Provider"
    SEEKER = "seeker", "Location Seeker"


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=UserRole.choices)
    is_verified = models.BooleanField(default=False)
    last_active = models.DateTimeField(auto_now=True)

    def deactivate_if_inactive(self):
        if self.last_active < now() - timedelta(days=30):
            self.is_active = False
            self.save()

    def __str__(self):
        return f"{self.last_name} {self.first_name} with {self.role} role."


class RecognitionRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50)
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests")
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    estimated_date = models.DateField(null=True, blank=True)
    estimated_location = models.CharField(max_length=255, blank=True)
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} provided by {self.provider}"


class Photo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(RecognitionRequest, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="photos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image from request: {self.request}"

class Answer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(RecognitionRequest, on_delete=models.CASCADE,related_name="answers")
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answers")
    latitude = models.FloatField()
    longitude = models.FloatField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.latitude} | {self.longitude}"
