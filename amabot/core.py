from collections import deque
from pprint import pprint
import json
import random
import time
import amabot.messenger as messenger
import amabot.config as config
from .models import ConversationModel, ImposterModel
from datetime import datetime

# reload module. initialize.
fan_requests = deque()
fan_requests_surfaced = []
chats = list()
is_inited = False


def init_core_if_necessary():
    global is_inited

    if is_inited:
        return
    is_inited = True

    # Thread to check request TTL.
    import threading

    ImposterModel.objects.all().update(is_free=True)

    def reroute_request(TTL=3600):
        '''
        if the request has been surfaced and not responsed in TTL seconds, 
            then it will be re-routed.
        '''
        print 'thread started.'
        global fan_requests_surfaced

        while True:
            time_now = datetime.now()
            for request in fan_requests_surfaced:
                print '[checking]', request['text']
                if (time_now - request['timestamp']).total_seconds() > TTL:
                    imposter = match_imposter(request) # match failed.
                    if imposter is not None:
                        print '[re-routed]', request['sender_id'], imposter.imposter_id
            time.sleep(30) 

    threading.Thread(target=reroute_request, kwargs=dict(TTL=1200)).start()


def print_global_stats():
    global fan_requests
    global fan_requests_surfaced
    global chats

    num_free_imposters = len(ImposterModel.objects.filter(is_free=True))
    print '[free imposters]', num_free_imposters
    print '[onging chats]', len(chats)
    print '[pending requests]', len(fan_requests)
    print '[surfaced requests]', len(fan_requests_surfaced)

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
    global chats

    (_type, endpoint) = endpoint_by_id(recipient_id)

    if _type == 'imposter': # add an imposter.
        if (filter(lambda chat: chat['imposter'] == sender_id, chats) or 
            ImposterModel.objects.filter(imposter_id=sender_id, imposter_page=recipient_id)):
            print 'imposter already exists', sender_id
        else:
            print 'imposter being added', sender_id
            ImposterModel(
                imposter_id=sender_id,
                imposter_page=recipient_id,
                is_free=True
            ).save()

    else: # add a fan.
        pass


def match_imposter(request): # match request with an free imposter.
    global chats

    free_imposters = ImposterModel.objects.filter(is_free=True)
    if len(free_imposters):
        imposter_id = random.randint(0, len(free_imposters)-1)
        imposter = free_imposters[imposter_id]
        chat = {
            'fan': request['sender_id'],
            'imposter': imposter.imposter_id,
            'fan_page': request['fan_page'],
            'imposter_page': imposter.imposter_page,
            'conversation': [
                {
                    'id': request['sender_id'],
                    'text': request['text']
                }
            ],
            'request': request
        }
        print '[match]', request['sender_id'], imposter.imposter_id
        imposter.is_free = False
        imposter.save()
        chats.append(chat)
        messenger.send_message(pageid=imposter.imposter_page, 
                     userid=imposter.imposter_id,
                     text=request['text'])
        #messenger.send_rating_page(pageid=imposter.imposter_page, 
        #             userid=imposter.imposter_id,
        #             text='how likely this person is to be Trump?')

        return imposter
    


def post_message(sender_id, recipient_id, text):
    global fan_requests
    global fan_requests_surfaced
    global chats

    (_type, endpoint) = endpoint_by_id(recipient_id)
    if _type == 'imposter': 
        active_chat = filter(lambda chat: chat['imposter'] == sender_id and chat['imposter_page'] == recipient_id,
                        chats)
        if len(active_chat) == 0: # no conversation available.
            print 'imposter: no active chat found'
            return
        assert len(active_chat) == 1
        active_chat = active_chat[0]
        if active_chat['request'] in fan_requests_surfaced:
            messenger.send_message(pageid=active_chat['fan_page'],
                                   userid=active_chat['fan'],
                                   text=text)
            fan_requests_surfaced.remove(active_chat['request'])
            print '[imposter] found active chat'
        else:
            print '[imposter] found active chat, but request invalid, still saving results.'

        # grow conversation data.
        active_chat['conversation'].append(
            {
                'id': sender_id,
                'text': text
            }
        )
        pprint(active_chat)
        conversation = ConversationModel(imposter_id=active_chat['imposter'],
                                    fan_id=active_chat['fan'],
                                    imposter_page=active_chat['imposter_page'],
                                    fan_page=active_chat['fan_page'],
                                    content=json.dumps(active_chat['conversation'])
                                    )
        conversation.save()
        
        if random.random() < config.RATING_PROB:
            messenger.send_rating_page(pageid=active_chat['fan_page'], 
                         userid=active_chat['fan'],
                         text='how\'s my answer? :)',
                         meta={'conversation_id': conversation.id})
        

        # conversation ends, and set imposters free.
        chats.remove(active_chat)
        imposter = ImposterModel.objects.get(
            imposter_id=active_chat['imposter'],
            imposter_page=active_chat['imposter_page']
        )
        imposter.is_free = True
        imposter.save()

        # feedback. how many conversations this imposter had.
        if random.random() < config.SCORE_PROB:
            past_conversations = ConversationModel.objects.filter(
                    imposter_page=active_chat['imposter_page'],
                    imposter_id=active_chat['imposter']
                )
            num_conversations = len(past_conversations)
            print 'num conversations', num_conversations
            if num_conversations % 1 == 0:
                score = [conversation.rating for conversation in past_conversations
                            if conversation.rating > 0]
                score = score[-20:]
                score = sum(score) / float(len(score))
                messenger.send_notification_page(
                        pageid=active_chat['imposter_page'],
                        userid=active_chat['imposter'],
                        text='Wow! your current imposter score is %0.1f / 3.0' % score
                    )


    elif _type == 'fan':
        fan_requests.append({
            'sender_id': sender_id,
            'fan_page': recipient_id,
            'text': text,
            'timestamp': datetime.now(),
        })
    # match fans to free imposters.
    while len(fan_requests):
        request = fan_requests.popleft()
        if match_imposter(request) is None: # match failed.
            fan_requests.appendleft(request)
            break
        else:
            fan_requests_surfaced.append(request)

    print_global_stats()

        
def handle_postback(sender_id, recipient_id, payload):
    try:
        payload = json.loads(payload)
        if 'rating' in payload:
            conversation_id = payload['conversation_id']
            conversation = ConversationModel.objects.get(id=conversation_id)
            conversation.rating = payload['rating']
            conversation.save()
            print '[postback] rating saved for ', conversation.id, conversation.content
            messenger.send_message(pageid=conversation.fan_page,
                                   userid=conversation.fan_id,
                                   text='thanks!')
        if 'notification' in payload:
            print '[postback] notification'
            messenger.send_message(pageid=recipient_id,
                                   userid=sender_id,
                                   text=':)')
    except:
        print '[postback] cannot handle payload', payload

