"""Views for geoguessr project"""
from django.forms import ValidationError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from verify_email.email_handler import ActivationMailManager


from .models import MilitaryPromote, Photo, RecognitionRequest, User
from .forms import (
    AnswerForm,
    RecognitionRequestForm,
    RegistrationForm,
    LoginForm,
)


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
            return redirect('/')
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

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                return HttpResponse('Disabled account')
            return HttpResponse('Invalid login')
    form = LoginForm()
    return render(request, 'login.html', {'form': form})


@login_required(login_url='login-page')
def logout_view(request):
    """
    Log out the user.

    This view logs out the current user and redirects to the login page.
    """
    logout(request)
    return redirect('login-page')


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
                Photo.objects.create(
                    recognition_request=recognition_request,
                    image=photo_file
                )
    else:
        form = RecognitionRequestForm()
    return render(request, 'create-request.html', {'form': form})


@login_required(login_url='login-page')
def show_recognition_requests(request):
    """
    Show all recognition requests.

    This view gets all recognition requests and shows them in a list.
    """
    recognition_requests = RecognitionRequest.objects.all()
    return render(
        request,
        'recognition_request_list.html',
        {'recog_requests': recognition_requests}
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

    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.seeker_id = request.user.id
            answer.recognition_request = recognition_request
            answer.save()
            return render(
                request,
                'location-details.html',
                {'recog_arg': recognition_request, 'form': form}
            )
    else:
        form = AnswerForm()
    return render(
        request,
        'location-details.html',
        {'recog_arg': recognition_request, 'form': form}
    )


@login_required(login_url='login-page')
def user_account(request):
    user = request.user
    recognition_requests = RecognitionRequest.objects.filter(provider=user)
    context = {
        'recognition_requests': recognition_requests,
    }
    return render(request, 'profile.html', context)


@login_required(login_url='login-page')
def military_promote(request):
    user = request.user
    is_request = bool(MilitaryPromote.objects.filter(seeker=user))
    if user.has_role('provider') or is_request:
        return redirect('account')
    MilitaryPromote.objects.create(seeker=user)
    return redirect('account')
