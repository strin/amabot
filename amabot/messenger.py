import requests
from access import access_token_by_pageid
import json

def send_message(pageid, userid, text):
    r = requests.post('https://graph.facebook.com/v2.6/me/messages?access_token=%s' % access_token_by_pageid[pageid],
                    json={
                        u'recipient': {u'id': userid},
                        u'message': {u'text': text},
                        u'notification_type': 'REGULAR'
                    }
            )

    if r.status_code == '200':
        return True
    return False


if __name__ == '__main__':
    send_message('1033841673375305', '113754149044475', text='hello, can you here me?')
