from django.shortcuts import render
from django.http import HttpResponse

from .models import Greeting
import sys

# Create your views here.
def index(request):
    # return HttpResponse('Hello from Python!')
    return render(request, 'index.html')


def webhook(request):
    if request.GET['hub.verify_token'] == 'amabot_is_awesome':
        return HttpResponse(request.GET['hub.challenge'])
    else:
        return HttpResponse('Error, invalid token')
