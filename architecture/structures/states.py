#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re

from architecture.actuators.messaging import send_message
from architecture.actuators.markov_message import generate_random_message

class State:

    def __init__(self, user_id, **kwargs):
        self.user_id = user_id
        self.next_states = []

    def run(self):
        pass

    def get_next_state(self, user_input, parser):
        pass

class InitState(State):

    def __init__(self, user_id, global_frame):
        State.__init__(self, user_id)
        self.global_frame = global_frame
        self.username = global_frame['CONTEXT']['first_name']

    def run(self):
        # if self.global_frame['CONTEXT']['intent'] == X:
        #     ans = generate_random_message(case=X)
        try:
            message = 'INTENT: {}'.format(self.global_frame['CONTEXT']['intent'])
            send_message(self.user_id, message)
        except:
            ans = generate_random_message()
            send_message(self.user_id, ans)

    def get_next_state(self, user_input, parser):
        try:
            intent = parser.intent_parse(user_input['MESSAGE'],
                                         intents=list(parser.intents.index))
            self.global_frame['CONTEXT']['intent'] = intent
        except:
            pass
        return self
        #if re.search('(queja)|(sugerencia)|(aclaraci[oó]n)', user_input['MESSAGE']):
        #    return Estado2(self.user_id, self.global_frame)
        #else:
        #    return Estado3(self.user_id, self.global_frame)

class Estado2(State):

    def __init__(self, user_id, global_frame):
        State.__init__(self, user_id)
        self.global_frame = global_frame
        self.username = global_frame['CONTEXT']['first_name']

    def run(self):
        message = 'Lo lamento {}, ¿te puedo ayudar con algo?'.format(self.username)
        send_message(self.user_id, message)

    def get_next_state(self, user_input):
        return InitState(self.user_id, self.global_frame)

class Estado3(State):

    def __init__(self, user_id, global_frame):
        State.__init__(self, user_id)
        self.global_frame = global_frame
        self.username = global_frame['CONTEXT']['first_name']

    def run(self):
        message = '🤡'.format(self.username)
        send_message(self.user_id, message)

    def get_next_state(self, user_input):
        return InitState(self.user_id, self.global_frame)