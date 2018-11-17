#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import itertools
import operator
import codecs
import random
import nltk
import os
import re

class TextGenerator(object):
    
    def __init__(self, data_list):
        self.text = self._load(data_list)
        self.text_tokens = self._prune(self._tokenize())
        self.states = list(set(self.text_tokens))
        self.possible_transitions = self._get_transitions()
        self.trasnsition_probabilites = self.train()
        self.total_words = 0.0
        
    def _load(self, files):
        text = " "
        for f in files:
            print('Reading {}'.format(f))
            with codecs.open(f, 'rb', 'utf-8') as infile:
                text += self._clean(infile.read().encode('utf-8').decode('ascii', 'ignore')).strip()
        return text
    
    def _get_possibilities(self, state):
        words = []
        for index, value in enumerate(self.text_tokens):
            if value == state:
                try:
                    words.append(self.text_tokens[index+1])
                except:
                    words.append('EOS')
        return {state: dict(collections.Counter(words))}
    
    def _add_probabilities(self, possibilities):
        temp = {}
        for possibility in possibilities:
            for k, v in possibility.items():
                temp[k] = [{'probab': (count/float(self.total_words)) * (1/float(len(v))), 'word': wrd} for wrd,count in v.items()]
        return temp
    
    def train(self):
        possibilities = []
        for state in self.states:
            possibilities.append(self._get_possibilities(state))
        probabilities = self._add_probabilities(possibilities)
        return probabilities
            
    def _get_transitions(self):
        return [[self.states] for state in self.states]
    
    def _prune(self, tokens):
        if len(tokens) > 100000:
            self.total_words = 100000
            return tokens[:self.total_words]
        self.total_words = len(tokens)
        return tokens
        
    def _clean(self, text):
        text = text.lower()
        text = re.sub(r"(\n|\t|/)", " ", text)
        text = re.sub(r'([.,/#!$%^&*;:{}=_`~()-])[.,/#!$%^&*;:{}=_`~()-]+', r'\1', text)
        text = re.sub('([.,!?()])', r' \1 ', text)
        return re.sub(r"\s{2,}", " ", text)
    
    def get_len(self, d):
        return len(d)
    
    def _tokenize(self):
        tokens = nltk.word_tokenize(self.text)
        return tokens

def formatter(s):
    s = s.split()
    # greedy sentence finisher (matches to last (.))
    s = ' '.join(s[:[idx for idx, ch in enumerate(s) if ch == '.'][-1]+1])
    s = s.capitalize()  # sentence casing
    s = re.sub(r'\s(\.|,|!|\?|\(|\)|\]|\[)', r'\1', s) # remove padded space before punc.
    return s

# Generator models
SALUDO_generator = TextGenerator(['data/saludos.txt'])

def generate_random_message(case='saludo'):
    if case == 'saludo':
        seed_word = SALUDO_generator.states[random.randint(0, len(SALUDO_generator.states) - 1)]
        story = [seed_word]
        words = 0
        max_words = 5
        randomness_level = 3

        while words < max_words-1:
            words += 1    
            candidates = SALUDO_generator.trasnsition_probabilites.get(seed_word)
            if candidates:
                temp = sorted(candidates, key=lambda c: c['probab'], reverse=True)
                candidates = [i.get('probab') for i in temp]
                grouped = sum([i[1] for i in [(k, sum(1 for i in g)) 
                                              for k,g in itertools.groupby(candidates)][:randomness_level]])
                seed_word = random.choice(temp[:grouped]).get('word')
                story.append(seed_word)
        return ' '.join(story)
    