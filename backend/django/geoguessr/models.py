"""Models for geoguessr"""
import secrets
import uuid
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


class UserRole(models.TextChoices):
    """
    User roles choices.
    """
    ADMIN = "admin", "Administrator"
    PROVIDER = "provider", "Photo Provider"
    SEEKER = "seeker", "Location Seeker"


class User(AbstractUser):
    """
    Custom user model that extends AbstractUser.

    This model adds extra fields such as a UUID primary key, email uniqueness,
    user role, verification status, and last active timestamp.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=UserRole.choices)
    is_verified = models.BooleanField(default=False)
    last_active = models.DateTimeField(auto_now=True)
    api_key = models.CharField(max_length=64, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = secrets.token_hex(32)  # генеруємо 64-символьний ключ
        super().save(*args, **kwargs)

    def deactivate_if_inactive(self):
        """
        Deactivate the user if inactive for more than 30 days.

        The user will be marked inactive if the last activity was over 30 days ago.
        """
        if self.last_active < now() - timedelta(days=30):
            self.is_active = False
            self.save()

    def has_role(self, role: str) -> bool:
        """Checks if users has needed role"""
        return role == self.role

    def __str__(self):
        """
        Return the string representation of the user.

        This returns the user's UUID as a string.
        """
        return str(self.id)


class RecognitionRequest(models.Model):
    """
    Model for a recognition request.

    This model stores data about a request made by a provider user.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50, unique=True)
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests")
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    estimated_date = models.CharField(max_length=25, null=True)
    estimated_location = models.CharField(max_length=255, blank=True)
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        """
        Return the string representation of the recognition request.

        This shows the title of the request and its provider.
        """
        return f"{self.title} provided by {self.provider}"


class Photo(models.Model):
    """
    Model for a photo.

    This model stores an image file related to a recognition request.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recognition_request = models.ForeignKey(
        RecognitionRequest,
        on_delete=models.CASCADE,
        related_name="photos"
    )
    image = models.ImageField(upload_to="geoguessr/photos")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Return the string representation of the photo.

        This shows the recognition request related to the image.
        """
        return f"Image from request: {self.recognition_request}"


class Answer(models.Model):
    """
    Model for an answer.

    This model stores an answer provided by a seeker user for a recognition request.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recognition_request = models.ForeignKey(
        RecognitionRequest,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answers")
    latitude = models.FloatField()
    longitude = models.FloatField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Return the string representation of the answer.

        This shows the latitude and longitude of the answer.
        """
        return f"{self.latitude} | {self.longitude}"


class MilitaryPromote(models.Model):
    """
    Model for military promote request
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="promote_request")

    def promote_user(self):
        seeker: User = self.seeker
        seeker.role = 'military'
        seeker.save()

        self.delete()
