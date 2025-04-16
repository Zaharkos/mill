"""Views for geoguessr project"""

import ultraimport
import struct
import base64

from django.contrib import messages
from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import MilitaryPromote, Photo, RecognitionRequest, User
from .forms import (
    AnswerForm,
    ChangeEmailForm,
    ChangePasswordForm,
    ChangeUsernameForm,
    RecognitionRequestForm,
    RegistrationForm,
    LoginForm,
)

Engine = ultraimport("__dir__/../../encryption/engine.py", "Engine")

'''
For now key is just hardcoded, could be randomly generated if saved somewhere
and will remain the same for encryption and decryption of some photos
'''

key = b'9991950:364322:4:4:7:2:1'

def request_list(request):
    """
    Show a list of published recognition requests.

    This view gets all posts that are published and shows them in a page.
    """
    posts = RecognitionRequest.published.all()
    return render(request, '<NOTHING>', {'posts': posts})

def main_page(request):
    """
    Show the main page.

    This view returns the main page template.
    """
    if request.user.is_authenticated:
        return redirect('recognation_request_list')
    return render(request, 'main.html')

def register_form(request):
    """
    Handle user registration.

    This view shows a registration form and processes the form.
    If the form is valid, it saves the new user and logs them in.
    """
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # user = ActivationMailManager.send_verification_link(request, form)
            user = form.save(commit=False)
            raw_password = form.cleaned_data.get("password")
            user.set_password(raw_password)
            user.role = 'seeker'
            user.save()
            return redirect('login-page')
        return render(request, "register.html", {"form": form})
    form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_form(request):
    """
    Handle user login.

    This view shows a login form and processes the form.
    If the form is valid, it checks the user and logs them in.
    """
    if request.user.is_authenticated:
        return redirect('account')

    error_messages = []

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('profile')
                error_messages.append('Account is disabled')
            error_messages.append('Invalid data')
    form = LoginForm()
    return render(request, 'login.html', {'form': form, 'error_messages': error_messages})

@login_required(login_url='login-page')
def logout_view(request):
    """
    Log out the user.

    This view logs out the current user and redirects to the login page.
    """
    logout(request)
    return redirect('login-page')

@login_required(login_url='login-page')
def profile(request):
    user = request.user

    # Встановлюємо початкові значення для форм
    username_form = ChangeUsernameForm(initial={'new_username': user.username})
    password_form = ChangePasswordForm(user=user)
    email_form = ChangeEmailForm(initial={'new_email': user.email})

    if request.method == "POST":
        if 'update_username' in request.POST:
            username_form = ChangeUsernameForm(request.POST)
            if username_form.is_valid():
                user.username = username_form.cleaned_data.get('new_username')
                user.save()
                messages.success(request, "Username обновлено успішно!")
                return redirect('profile')
        elif 'update_password' in request.POST:
            password_form = ChangePasswordForm(user, request.POST)
            if password_form.is_valid():
                user.set_password(password_form.cleaned_data.get('new_password'))
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Пароль обновлено успішно!")
                return redirect('profile')
        elif 'update_email' in request.POST:
            email_form = ChangeEmailForm(request.POST)
            if email_form.is_valid():
                user.email = email_form.cleaned_data.get('new_email')
                user.save()
                messages.success(request, "Email оновлено успішно!")
                return redirect('profile')

    context = {
        "username_form": username_form,
        "password_form": password_form,
        "email_form": email_form,
        "user": user,
    }

    return render(request, 'profile.html', context)

@login_required(login_url='login-page')
def create_recognition_request(request):
    """
    Create a new recognition request.

    This view handles the form to create a new recognition request.
    If the user is not valid, it redirects to the login page.
    When the form is valid, it saves the request and any photos.
    """
    if not isinstance(request.user, User):
        return redirect('login-page')
    if request.method == 'POST':
        form = RecognitionRequestForm(request.POST)

        if form.is_valid():
            recognition_request = form.save(commit=False)
            recognition_request.provider = request.user
            recognition_request.save()

            photos = request.FILES.getlist('photos')
            for photo_file in photos:
                byte_data = photo_file.read()
                photo_file.seek(0)
                photo_file.write(Engine().encode(byte_data, key))
                Photo.objects.create(
                    recognition_request=recognition_request,
                    image=photo_file
                )
            return redirect('recognation_request', pk=recognition_request.id)
    else:
        form = RecognitionRequestForm()
    return render(request, 'create-request.html', {'form': form})

@login_required(login_url='login-page')
def show_recognition_requests(request):
    """
    Show all recognition requests.

    This view gets all recognition requests and shows them in a list.
    """
    recognition_requests_list = RecognitionRequest.objects.filter(is_visible=True)
    paginator = Paginator(recognition_requests_list, 10)
    page_number = request.GET.get('page')
    recognition_requests = paginator.get_page(page_number)

    return render(
        request,
        'recognition_request_list.html',
        {'recognition_requests': recognition_requests}
    )

@login_required(login_url='login-page')
def get_recognition_request(request, pk):
    """
    Get a recognition request and add an answer.

    This view retrieves a recognition request by its primary key.
    If a POST request with a valid form is received, it saves the answer.
    """
    try:
        recognition_request = get_object_or_404(RecognitionRequest, pk=pk)
    except ValidationError:
        return redirect('recognation_request_list')

    if not recognition_request.is_visible:
        return redirect('recognation_request_list')

    decoded_photos = []
    for photo in recognition_request.photos.all():
        image_field = photo.image

        image_field.open(mode='rb')
        byte_data = image_field.read()
        image_field.close()

        decoded_data = Engine().decode(byte_data, key)
        decoded_photos.append(base64.b64encode(decoded_data).decode('utf-8'))

    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.seeker_id = request.user.id
            answer.recognition_request = recognition_request
            answer.longitude = Engine().encode(answer.longitude, key)
            answer.latitude = Engine().encode(answer.latitude, key)
            answer.save()
            return render(
                request,
                'location-details.html',
                {
                    'req': recognition_request,
                    'form': form,
                    'decoded_photos': decoded_photos
                }
            )
    else:
        form = AnswerForm()

    return render(
        request,
        'location-details.html',
        {
            'req': recognition_request,
            'form': form,
            'decoded_photos': decoded_photos,
        }
    )

@login_required(login_url='login-page')
def military_request_list(request):
    user = request.user
    if user.has_role('seeker'):
        return redirect('profile')

    recognition_requests_list = RecognitionRequest.objects.filter(provider=user)
    paginator = Paginator(recognition_requests_list, 10)
    page_number = request.GET.get('page')
    recognition_requests = paginator.get_page(page_number)

    context = {
        'recognition_requests': recognition_requests,
    }
    return render(request, 'military-requests.html', context)

@login_required(login_url='login-page')
def recognition_request_details(request, pk):
    try:
        recognition_request = get_object_or_404(RecognitionRequest, pk=pk)
    except ValidationError:
        return redirect('recognation_request_list')
    user = request.user
    if recognition_request.provider != user:
        return Http404()

    decrypted_coords = []
    for coords in recognition_request.answers.all():
        coords.longitude = struct.unpack(">d", Engine().decode(coords.longitude, key))[0]
        coords.latitude = struct.unpack(">d", Engine().decode(coords.latitude, key))[0]
        decrypted_coords.append(coords)

    context = {
        'req': recognition_request,
        'decrypt_coords': decrypted_coords
    }
    return render(request, 'military-request-details.html', context)

@login_required(login_url='login-page')
def recognition_request_close(request, pk):
    try:
        recognition_request = get_object_or_404(RecognitionRequest, pk=pk)
    except ValidationError:
        return redirect('account')
    user = request.user
    if recognition_request.provider != user:
        return Http404()

    recognition_request.is_visible = False
    recognition_request.save()
    return redirect('account')

@login_required(login_url='login-page')
def military_promote(request):
    user = request.user
    if not user.has_role('seeker'):
        return redirect('profile')
    is_request = bool(MilitaryPromote.objects.filter(seeker=user))
    if user.has_role('provider') or is_request:
        return redirect('profile')
    MilitaryPromote.objects.create(seeker=user)
    return redirect('profile')

@login_required(login_url='login-page')
def admin_panel(request):
    user = request.user
    if not user.has_role('admin'):
        return redirect('recognation_request_list')

    promotes_list = MilitaryPromote.objects.all()
    paginator = Paginator(promotes_list, 10)
    page_number = request.GET.get('page')
    promotes = paginator.get_page(page_number)
    return render(request, 'admin.html', {'promotes': promotes})

@login_required(login_url='login-page')
def accept_promote(request, pk):
    user = request.user
    if not user.has_role('admin'):
        return redirect('recognation_request_list')
    promote = MilitaryPromote.objects.get(id=pk)
    promote.promote_user()
    return redirect('admin-panel')

@login_required(login_url='login-page')
def decline_promote(request, pk):
    user = request.user
    if not user.has_role('admin'):
        return redirect('recognation_request_list')
    promote = MilitaryPromote.objects.get(id=pk)
    return redirect('admin-panel')
