from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import RecognitionRequest
from .forms import RegistrationForm, LoginForm
from django.contrib.auth import authenticate, login, logout

def request_list(request):
    posts = RecognitionRequest.published.all()
    return render(request, '<NOTHING>', {'posts': posts})

def main_page(request):
    return render(request, 'main.html')

def register_form(request):    
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
        else:
            return render(request, "register.html", {"form": form})
    else:
        form = RegistrationForm()
        return render(request, 'register.html', {'form':form})

def login_form(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                return HttpResponse('Disabled account')
            return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login-page')
