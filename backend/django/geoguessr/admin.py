from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, RecognitionRequest, Photo, Answer

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'email', 'role', 'is_active', 'last_active')
    search_fields = ('username', 'email', 'role')

@admin.register(RecognitionRequest)
class RecognitionRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'provider', 'created_at', 'estimated_date', 'estimated_location', 'is_visible')
    list_filter = ('is_visible', 'created_at', 'estimated_date')
    search_fields = ('description', 'estimated_location', 'provider__username')

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'recognition_request', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('request__description',)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'recognition_request', 'seeker', 'latitude', 'longitude', 'submitted_at')
    list_filter = ('submitted_at',)
    search_fields = ('request__description', 'seeker__username')
