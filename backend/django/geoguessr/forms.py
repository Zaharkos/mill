import re
from django.core.exceptions import ValidationError
from django import forms
from .models import Answer, RecognitionRequest, User
import struct
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
        fields = ['title', 'estimated_date', 'estimated_location', 'description']

        widgets = {
            'title': forms.TextInput(attrs={
                'id': 'title',
                'class': 'form-control',
            }),
            'estimated_date': forms.Textarea(attrs={
                'id': 'estimated_date',
                'class': 'form-control',
            }),
            'estimated_location': forms.Textarea(attrs={
                'id': 'estimated_location',
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'id': 'description',
                'class': 'form-control',
            }),
        }


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
    """
    # form‐level fields for user input
    latitude  = forms.FloatField(widget=forms.HiddenInput(attrs={'id': 'lat'}))
    longitude = forms.FloatField(widget=forms.HiddenInput(attrs={'id': 'lng'}))

    class Meta:
        model = Answer
        # we’re *not* including the model’s ByteFields here,
        # since we handle them manually
        fields = []

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get('latitude')
        lng = cleaned.get('longitude')

        # standard range checks
        if lat is None:
            self.add_error('latitude', 'Latitude is required.')
        elif not (-90 <= lat <= 90):
            self.add_error('latitude', 'Latitude must be between -90 and 90.')

        if lng is None:
            self.add_error('longitude', 'Longitude is required.')
        elif not (-180 <= lng <= 180):
            self.add_error('longitude', 'Longitude must be between -180 and 180.')

        # if there are any field errors, bail out early
        if self.errors:
            return cleaned

        # pack each float as an 8‐byte big‑endian double
        # you can adjust format ('>f' for 4‐byte float) if you prefer
        self.instance.latitude  = struct.pack('>d', lat)
        self.instance.longitude = struct.pack('>d', lng)

        return cleaned

    def save(self, commit=True):
        # by now instance.latitude/longitude are bytes,
        # so the ByteField will accept them cleanly
        return super().save(commit=commit)


class ChangeUsernameForm(forms.Form):
    new_username = forms.CharField(
        max_length=150,
        label="New Username",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter new username'})
    )

    def clean_new_username(self):
        username = self.cleaned_data.get('new_username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Ім'я користувача вже існує.")
        if not re.match(r'^\w+$', username):
            raise ValidationError("Імʼя користувача може містити лише цифри, літери та нижні підкреслення.")
        return username

class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter current password'})
    )
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'})
    )
    confirm_password = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'})
    )

    def __init__(self, user, *args, **kwargs):
        """
        Зберігаємо поточного користувача для перевірки поточного пароля.
        """
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise ValidationError("Невірний поточний пароль.")
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        # Перевірка довжини та змісту нового пароля
        if new_password:
            if len(new_password) < 8:
                self.add_error("new_password", "Пароль має містити мінімум 8 символів.")
            if not any(char.isdigit() for char in new_password):
                self.add_error("new_password", "Пароль має містити хоча б 1 цифру.")
            if not any(char.isalpha() for char in new_password):
                self.add_error("new_password", "Пароль має містити хоча б 1 букву.")

        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError("Паролі не співпадають.")

        return cleaned_data



class ChangeEmailForm(forms.Form):
    new_email = forms.EmailField(
        label="New Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter new email'})
    )

    def clean_new_email(self):
        new_email = self.cleaned_data.get("new_email")
        if User.objects.filter(email=new_email).exists():
            raise ValidationError("Ця адреса вже є зайнятою.")
        return new_email