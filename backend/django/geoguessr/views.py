from django.shortcuts import render
from .models import RecognitionRequest

def request_list(request):
    posts = RecognitionRequest.published.all()
    # TODO: page with requests
    return render(request, '<NOTHING>', {'posts': posts}) 
