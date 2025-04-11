import re
from django.core.exceptions import ValidationError
from django import forms
from .models import Answer, RecognitionRequest, User

class MultipleFileInput(forms.ClearableFileInput):
    """
    A widget that allows the selection of multiple files.
    """
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """
    A file field that accepts multiple files.

    This field uses the MultipleFileInput widget by default and
    cleans the input data to handle multiple file uploads.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the field with a widget that supports multiple files.
        """
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        """
        Clean the input data and return a list of cleaned files.

        If the data is a list or tuple, each file is cleaned individually.
        Otherwise, a single file is cleaned.
        """
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class RecognitionRequestForm(forms.ModelForm):
    """
    Form for creating or updating a recognition request.

    This form includes an extra field for uploading multiple photos.
    """
    photos = MultipleFileField(label='Select files', required=True)

    class Meta:
        model = RecognitionRequest
        fields = ['title', 'description', 'estimated_date', 'estimated_location']

    def save(self, commit=True, provider=None):
        """
        Save the recognition request instance.

        If a provider is given, it is set on the instance before saving.
        """
        recognition_request = super().save(commit=False)
        if provider:
            recognition_request.provider = provider
        if commit:
            recognition_request.save()
        return recognition_request


class RegistrationForm(forms.ModelForm):
    """
    Form for user registration.

    This form collects basic user information and validates the username,
    email, and password fields.
    """
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={'id': 'email', 'placeholder': 'Enter email'}),
            'password': forms.PasswordInput(attrs={'id': 'password', 'placeholder': 'Enter password'})
        }
        help_texts = {
            'username': None,
        }

    def clean_username(self):
        """
        Validate the username.

        The username must not already exist and must contain only digits,
        letters, or underscores.
        """
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Імʼя користувача вже існує")
        if not re.match(r'^\w+$', username):
            raise ValidationError(
                "Імʼя користувача може містити лише цифри, літери та нижні підкреслення."
            )
        return username

    def clean_email(self):
        """
        Validate the email.

        The email must be unique among all users.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ця адреса вже є зайнятою.")
        return email

    def clean_password(self):
        """
        Validate the password.

        The password must be at least 8 characters long and contain at least one digit
        and one letter.
        """
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError("Пароль має містити мінімум 8 символів")
        if not any(char.isdigit() for char in password):
            raise ValidationError("Пароль має містити хоча б 1 цифру")
        if not any(char.isalpha() for char in password):
            raise ValidationError("Пароль має містити хоча б 1 букву")
        return password


class LoginForm(forms.Form):
    """
    Form for user login.

    This form requires a username and a password.
    """
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class AnswerForm(forms.ModelForm):
    """
    Form for providing an answer to a recognition request.

    This form collects the latitude and longitude as text inputs.
    """
    class Meta:
        model = Answer
        fields = ['latitude', 'longitude']
        widgets = {
            'latitude': forms.HiddenInput(attrs={'id': 'lat', 'step': 'any'}),
            'longitude': forms.HiddenInput(attrs={'id': 'lng', 'step': 'any'}),
        }
        hidden = ['latitude', 'longitude']
