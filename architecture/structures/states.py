#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re
import random

from architecture.actuators.messaging import send_message
from architecture.actuators.markov_message import generate_random_message

from architecture.sensors.sentiment import predict_sentiment

MOVIE_LIST = [
    'Titanic', 
    'War of the Worlds',
    'Interstellar',
    '2001: A Space Odyssey',
    'Star Wars',
    'Blade Runner'
]

class State:

    def __init__(self, user_id, **kwargs):
        self.user_id = user_id
        self.actions = []

    def run(self):
        for action in self.actions:
            action()

    def get_next_state(self, user_input, parser):
        pass

    def join(self, other_state):
        self.actions += other_state.actions
        self.get_next_state = other_state.get_next_state
        return self
        

class InitState(State):

    def __init__(self, user_id, global_frame):
        State.__init__(self, user_id)
        self.global_frame = global_frame
        self.username = global_frame['CONTEXT']['first_name']
        self.actions = [self.say_hello, self.ask_for_movie]
        
    def say_hello(self):
        send_message(self.user_id, 'Hello, {}! '.format(self.username))

    def ask_for_movie(self):
        movie_i = random.randint(0, len(MOVIE_LIST) - 1)
        movie = MOVIE_LIST[movie_i]
        message = 'What do you think about {}?'.format(movie)
        send_message(self.user_id, message)
        
    def get_next_state(self, user_input):
        if predict_sentiment(user_input['MESSAGE']) == 0:
            return EstadoNeg(self.user_id, self.global_frame)
        else:
            return EstadoPos(self.user_id, self.global_frame)

class Estado2(State):

    def __init__(self, user_id, global_frame):
        State.__init__(self, user_id)
        self.global_frame = global_frame
        self.username = global_frame['CONTEXT']['first_name']
        self.actions = [self.respond]
        
    def respond(self):
        movie_i = random.randint(0, len(MOVIE_LIST) - 1)
        movie = MOVIE_LIST[movie_i]
        message = 'What do you think about {}?'.format(movie)
        send_message(self.user_id, message)

    def get_next_state(self, user_input):
        if predict_sentiment(user_input['MESSAGE']) == 0:
            return EstadoNeg(self.user_id, self.global_frame)
        else:
            return EstadoPos(self.user_id, self.global_frame)

class EstadoNeg(State):

    def __init__(self, user_id, global_frame):
        State.__init__(self, user_id)
        self.global_frame = global_frame
        self.username = global_frame['CONTEXT']['first_name']
        self.actions = [self.respond]
        self.next_state = self.join(Estado2(self.user_id, self.global_frame))

    def respond(self):
        message = 'Thank you, I\'ll never watch it'.format(self.username)
        send_message(self.user_id, message)

    def get_next_state(self, user_input):
        return self.next_state

class EstadoPos(State):

    def __init__(self, user_id, global_frame):
        State.__init__(self, user_id)
        self.global_frame = global_frame
        self.username = global_frame['CONTEXT']['first_name']
        self.actions = [self.respond]
        self.next_state = self.join(Estado2(self.user_id, self.global_frame))

    def respond(self):
        message = 'Great, I\'ll watch it tonight'.format(self.username)
        send_message(self.user_id, message)

    def get_next_state(self, user_input):
        return self.next_state