#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Classes and functions to clean out text in Mexican Spanish.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re
import os
import codecs

STOPWORD_FILE = 'data/stopwords-es.txt'

ACCENTS = {'á': 'a',
           'é': 'e',
           'í': 'i',
           'ó': 'o',
           'ú': 'u'}

def remove_accents(phrase):
    """Simple Spanish accent remover.
    """
    new = phrase
    for acc, non in ACCENTS.items():
        new = new.replace(acc, non)
        new = new.replace(acc.upper(), non.upper())
    return new

class NLCleaner:
    """A natural language cleaner, based in stopwords.
    Stemming should be added soon!
    """

    def __init__(self, stopwords=STOPWORD_FILE):
        """Default constructor, given a stopword filepath.
        """
        assert os.path.exists(stopwords)
        self.stopw_regex = []
        self.stopwords = []
        with codecs.open(stopwords, 'r', encoding='utf-8') as fil:
            lines = [l.encode('utf-8').decode().strip() for l in fil]
            for line in lines:
                line = line.strip().lower()
                self.stopwords.append(line)
                if re.match(r'\w', line):
                    self.stopw_regex.append('(\\b{}\\b)'.format(line))
                else:
                    self.stopw_regex.append('({})'.format(line))

        if self.stopw_regex:
            self.stopw_regex = re.compile('({})'.format('|'.join(self.stopw_regex)))
        else:
            print('[WARNING] No stopword detected!')

    def remove_stopwords_text(self, text):
        """Remove all the found stopwords in a given string.
        """
        if not self.stopw_regex:
            print('[WARNING] No stopword detected!')
            return text
        else:
            res = remove_accents(text.lower())
            res = self.stopw_regex.sub('', res)
            res = re.sub(r'\s{2,}', ' ', res).strip()
            return res

    def remove_stopwords_corpus(self, corpus):
        """Removes all the stopwords in a list of strings.
        """
        if not self.stopw_regex:
            print('[WARNING] No stopword detected!')
            return None
        else:
            cleaned = []
            for line in corpus:
                res = self.remove_stopwords_text(line)
                cleaned.append(res)
            return cleaned
