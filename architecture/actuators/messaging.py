#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import json
import requests

# Base URL to get user info: needs to be formatted with
# a sender_id and the page access token.
INFO_URL = 'https://graph.facebook.com/v2.6/{}?fields=first_name,last_name,profile_pic&access_token={}'

def send_message(recipient_id, message_text, quick_replies=None):
    """
    Message sending function wrapper
    """
    print('sending message to {recipient}: {text}'.format(recipient=recipient_id, text=message_text))

    params = {
        'access_token': os.environ['PAGE_ACCESS_TOKEN']
    }
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'messaging_type': 'RESPONSE',
        'recipient': {
            'id': recipient_id
        },
        'message':
        {
            'text': message_text
        }
    }
    if quick_replies:
        data['message']['quick_replies'] = quick_replies
    data = json.dumps(data)
    req = requests.post('https://graph.facebook.com/v2.6/me/messages?access_token={}'.format(os.environ['PAGE_ACCESS_TOKEN']),
                        params=params,
                        headers=headers,
                        data=data)
    if req.status_code != 200:
        print(req.status_code)
        print(req.text)