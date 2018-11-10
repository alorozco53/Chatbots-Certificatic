#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from architecture.structures.states import State

class FSM:
    """Máquina de estados
    """
    def __init__(self, current_state):
        # compatibilidad
        assert isinstance(current_state, State)

        # estado actual
        self.current_state = current_state

    def run(self):
        self.current_state.run()

    def transition(self, user_input):
        self.current_state = self.current_state.get_next_state(user_input)