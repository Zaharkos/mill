import re
from django.core.exceptions import ValidationError
from django import forms
from .models import RecognitionRequest, Photo, User

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class RecognitionRequestForm(forms.ModelForm):
    photos = MultipleFileField(label='Select files', required=False)

    class Meta:
        model = RecognitionRequest
        fields = ['description', 'estimated_date', 'estimated_location', 'is_visible']

    def save(self, commit=True, provider=None):
        recognition_request = super().save(commit=False)
        if provider:
            recognition_request.provider = provider
        if commit:
            recognition_request.save()
            photos = self.files.getlist('photos')
            for photo_file in photos:
                Photo.objects.create(request=recognition_request, image=photo_file)
        return recognition_request


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={'id': 'email', 'placeholder': 'Enter email'}),
        }
        help_texts = {
            'username': None,
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Імʼя користувача вже існує")
        if not re.match(r'^\w+$', username):
            raise ValidationError("Імʼя користувача може містити лише цифри, \
літери та нижні підкреслення.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ця адреса вже є зайнятою.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError("Пароль має містити мінімум 8 символів")
        if not any(char.isdigit() for char in password):
            raise ValidationError("Пароль має містити хоча б 1 цифру")
        if not any(char.isalpha() for char in password):
            raise ValidationError("Пароль має містити хоча б 1 букву")
        return password


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
