from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from .models import Greeting
import json
import sys
from pprint import pprint

from .core import post_message, add_user 

sys.stdout = sys.stderr
# Create your views here.
def index(request):
    # return HttpResponse('Hello from Python!')
    return render(request, 'index.html')


class WebhookView(generic.View):
    def get(self, request, *args, **kwargs):
        if request.GET['hub.verify_token'] == 'amabot_is_awesome':
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events 
                print '-----------------message-----------------'
                pprint(message)
                print '-----------------------------------------'
                if 'message' in message:
                    # Print the message to the terminal
                    post_message(message['sender']['id'], message['recipient']['id'], message['message']['text'])
                else: # start a new conversation, exciting!
                    add_user(message['sender']['id'], message['recipient']['id'])


        return HttpResponse()

_webhook_view = WebhookView.as_view()

@csrf_exempt
def webhook_view(request):
    return _webhook_view(request)

