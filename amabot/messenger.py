# -*- coding: utf-8 -*-

import requests
from access import access_token_by_pageid
import json

def send_message(pageid, userid, text, attachment=None):
    message = {}
    if text:
        message.update({u'text': text})
    if attachment:
        message.update({u'attachment': attachment})

    r = requests.post('https://graph.facebook.com/v2.6/me/messages?access_token=%s' % access_token_by_pageid[pageid],
                    json={
                        u'recipient': {u'id': userid},
                        u'message': message,
                        u'notification_type': 'REGULAR'
                    }
            )

    if r.status_code == '200':
        return True
    
    print r.content
    return False


def send_rating_page(pageid, userid, text, meta={}):
    encode_rating = lambda rating: json.dumps(
                dict(rating=rating, **meta)
            )
    attachment = {
      'type': 'template',
      'payload':{
        'template_type': 'button',
        "text":text,
        "buttons":[
          {
            "type":"postback",
            "title":u'\u2605\u2605\u2605',
            "payload": encode_rating(3)
          },
          {
            "type":"postback",
            "title":u'\u2605\u2605',
            "payload": encode_rating(2)
          },
          {
            "type":"postback",
            "title":u'\u2605',
            "payload": encode_rating(1)
          }
        ]
      }
    }
    return send_message(pageid, userid, text=None, attachment=attachment)


def send_notification_page(pageid, userid, text, meta={}):
    attachment = {
      'type': 'template',
      'payload':{
        'template_type': 'button',
        "text":text,
        "buttons":[
          {
            "type":"postback",
            "title":u'okay',
            "payload": json.dumps(dict(notification='true',
                **meta))
          }
        ]
      }
    }
    return send_message(pageid, userid, text=None, attachment=attachment)


if __name__ == '__main__':
    send_message('1033841673375305', '113754149044475', text='hello, can you here me?')
