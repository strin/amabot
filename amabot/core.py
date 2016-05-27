from collections import deque
from pprint import pprint
import json
import amabot.messenger as messenger
from .models import Conversation

imposters_free = deque()
fan_requests = deque()
chats = list()

def endpoints():
    '''
    return a list of (imposter, fan).
    '''
    with open('imposter-fan.txt', 'r') as f:
        lines = f.readlines()
        lines = [unicode(line) for line in lines if len(line) > 0]
        endpoints = [line.replace('\n', '').split(' ') for line in lines]
    return endpoints


def endpoint_by_id(recipient_id):
    _endpoints = endpoints()
    _endpoints_by_first = [ep for ep in _endpoints if ep[0] == recipient_id]
    _endpoints_by_second = [ep for ep in _endpoints if ep[1] == recipient_id]
    assert len(_endpoints_by_first) + len(_endpoints_by_second) == 1
    if len(_endpoints_by_first) > 0:
        return ('imposter', _endpoints_by_first[0])
    else:
        return ('fan', _endpoints_by_second[0])


def add_user(sender_id, recipient_id, timestamp=None):
    '''
    start a conversation session.
    '''
    global imposters_free
    global chats

    (_type, endpoint) = endpoint_by_id(recipient_id)

    if _type == 'imposter': # add an imposter.
        if (filter(lambda chat: chat['imposter'] == sender_id, chats) or 
            filter(lambda imposter: imposter['sender_id'] == sender_id, imposters_free)):
            print 'imposter already exists', sender_id
        else:
            print 'imposter being added', sender_id
            imposters_free.append({
                'sender_id': sender_id,
                'imposter_page': recipient_id
            })
    else: # add a fan.
        pass


def post_message(sender_id, recipient_id, text):
    global imposters_free
    global fan_requests
    global chats

    print '[free imposters]', len(imposters_free),
    print '[onging chats]', len(chats)
    print '[pending requests]', len(fan_requests)

    (_type, endpoint) = endpoint_by_id(recipient_id)
    if _type == 'imposter': 
        active_chat = filter(lambda chat: chat['imposter'] == sender_id and chat['imposter_page'] == recipient_id,
                        chats)
        if len(active_chat) == 0: # no conversation available.
            print 'imposter: no active chat found'
            return
        assert len(active_chat) == 1
        active_chat = active_chat[0]
        messenger.send_message(pageid=active_chat['fan_page'],
                               userid=active_chat['fan'],
                               text=text)
        print 'imposter: found active chat'
        pprint(active_chat)
        # grow conversation data.
        active_chat['conversation'].append(
            {
                'id': sender_id,
                'text': text
            }
        )
        conversation = Conversation(imposter_id=active_chat['imposter'],
                                    fan_id=active_chat['fan'],
                                    imposter_page=active_chat['imposter_page'],
                                    fan_page=active_chat['fan_page'],
                                    content=json.dumps(active_chat['conversation'])
                                    )
        conversation.save()

        # conversation ends.
        chats.remove(active_chat)
        imposters_free.append({
            'sender_id': active_chat['imposter'],
            'imposter_page': active_chat['imposter_page']
        })
    elif _type == 'fan':
        fan_requests.append({
            'sender_id': sender_id,
            'fan_page': recipient_id,
            'text': text
        })
    # match fans to free imposters.
    while len(imposters_free) and len(fan_requests):
        request = fan_requests.popleft()
        imposter = imposters_free.popleft()
        chat = {
            'fan': request['sender_id'],
            'imposter': imposter['sender_id'],
            'fan_page': request['fan_page'],
            'imposter_page': imposter['imposter_page'],
            'conversation': [
                {
                    'id': request['sender_id'],
                    'text': request['text']
                }
            ]
        }
        print '[match]', request['sender_id'], imposter['sender_id']
        chats.append(chat)
        messenger.send_message(pageid=imposter['imposter_page'], 
                     userid=imposter['sender_id'],
                     text=request['text'])


            


    
    




def says_imposter(sender_id):
    global chat_by_imposter
    chat = chat_by_imposter[sender_id]
    if chat is None: # ignored.
        return
    
