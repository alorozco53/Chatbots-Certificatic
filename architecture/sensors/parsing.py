#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""A symbolic and statistical natural language parser is implemented here.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from architecture.sensors.cleaning import NLCleaner, remove_accents

CLEANER = NLCleaner()
VECTORIZER = TfidfVectorizer(analyzer='char',
                             tokenizer=CLEANER.remove_stopwords_text,
                             ngram_range=(2, 4))

class NLParser:
    """Wrapper class for all parsing algorithms.
    """

    def __init__(self, intent_data=None):
        """Intents and entities are encouraged to be provided
        in order to save memory in further computations.
        Data can be passed as a CSV file, formatted according to the docs.
        """
        if intent_data is not None:
            if isinstance(intent_data, dict):
                self.intents = pd.DataFrame(intent_data)
            else:
                self.intents = pd.read_csv(intent_data,
                                           names=['DOC', 'INTENT'],
                                           encoding='utf-8')
            self._build_intents()

    def _group_intents(self):
        """Groups text examples according to the same intent."""
        assert hasattr(self, 'intents')

        whole_corpus = []
        for intent in set(self.intents.INTENT):
            doc = ' '.join(self.intents.DOC[self.intents.INTENT == intent])
            whole_corpus.append([intent, doc])

        whole_corpus = pd.DataFrame(whole_corpus,
                                    columns=['INTENT', 'DOC'])
        self.intents = whole_corpus.set_index('INTENT')

    def _augment_intents(self):
        """Augments the current intent dataset
        by adding lemmatized words.
        """
        try:
            assert hasattr(self, 'intents')
        except:
            raise Exception('[ERROR] Intent list not defined!')
        print('Augmenting intent dataset...')
        aug = []
        for _, row in self.intents.iterrows():
            phrase = row.DOC
            doc = self.nlp(phrase)
            augmented = phrase + ' ' + ' '.join([' ' + token.lemma_
                                                 for token in doc])
            aug.append(augmented)

        aug = pd.DataFrame({'DOC': aug}, index=self.intents.index)
        self.intents = aug
        print('DONE')

    def _create_regex(self):
        """
        Creates a regular expression per each intent (according to each list of keywords).
        A list of keywords is automatically built depending on POS tag.
        """
        try:
            assert hasattr(self, 'intents')
        except:
            raise Exception('[ERROR] Intent list not defined!')

        # create regex for all intent examples
        intents_regex = []
        for _, row in self.intents.iterrows():
            phrase = str(row.DOC)
            keywords = []
            if len(phrase.split()) > 3:
                doc = self.nlp(phrase)
                for token in doc:
                    if token.pos_ in ['VERB', 'NOUN', 'ADJ', 'ADP', 'ADV']:
                        tok = str(token)
                        if tok not in keywords:
                            keywords.append(tok)
                keywords = CLEANER.remove_stopwords_corpus(keywords)
            else:
                keywords = phrase.split()
            spl = ['(\\b{}\\b)'.format(str(w.strip())) for w in keywords if w.strip()]
            regex = '|'.join(spl)
            regex = re.compile(regex)
            intents_regex.append(regex)

        # update intents
        self.intents['REGEX'] = pd.Series(intents_regex,
                                          index=self.intents.index)

    def _build_intents(self):
        """Builds the intent pd.DataFrame adding regexes and adding words.
        """
        try:
            assert hasattr(self, 'intents')
        except:
            raise Exception('[ERROR] Intent list not defined!')
        print('Augmenting intent internal representation...')
        whole_corpus = pd.DataFrame()
        for intent in set(self.intents.INTENT):
            # grab the corresponding examples
            examples = self.intents.DOC[self.intents.INTENT == intent]

            # build dataset
            phrase = ' '.join(CLEANER.remove_stopwords_corpus(examples))

            # build the corresponding regex
            examples = list(examples)
            keywords = []
            for ex in examples:
                keyw = remove_accents(ex.lower())
                keyw = re.sub(r'[^\w\s]', ' ', keyw).split()
                keywords.append(' '.join(keyw))
            spl = [r'(\\b{}\\b)'.format(str(w.strip())) for w in keywords if w.strip()]
            regex = '|'.join(spl)
            regex = re.compile(regex)

            # update intent corpus
            newrow = pd.DataFrame({'DOC': phrase,
                                   'REGEX': regex},
                                  index=[intent])
            whole_corpus = whole_corpus.append(newrow)
        self.intents = whole_corpus
        print('DONE')


    def _build_keywords(self):
        """
        Build keywords automatically, by extracting nouns, verbs and adjectives out of
        the examples.
        """
        try:
            assert hasattr(self, 'intents')
        except:
            raise Exception('[ERROR] Intent list not defined!')

        # construct keywords
        keywords = []
        for _, row in self.intents.iterrows():
            phrase = str(row.DOC)
            doc = self.nlp(phrase)
            doc_keywords = []
            for token in doc:
                if token.pos_ in ['VERB', 'NOUN', 'ADJ', 'ADP', 'ADV']:
                    tok = str(token)
                    if tok not in doc_keywords:
                        doc_keywords.append(tok)
            keywords.append(doc_keywords)

        # update intents
        self.intents['KEYWORDS'] = pd.Series(keywords)


    def _slice_intents(self, key):
        """Returns a pandas DataFrame according to the given intent key (or list of keys).
        """
        try:
            assert hasattr(self, 'intents')
        except:
            raise Exception('[ERROR] Intent list not defined!')

        if isinstance(key, str):
            if key not in self.intents.index.values:
                raise KeyError('[ERROR] Given key ({}) is not defined in intent DataFrame'.format(key))
            else:
                return self.intents[self.intents.index == key]
        else:
            sliced = pd.DataFrame()
            for k in key:
                if k not in self.intents.index.values:
                    raise KeyError('[ERROR] Given key ({}) is not defined in intent DataFrame'.format(k))
                else:
                    sliced = sliced.append(self.intents[self.intents.index == k])
            return sliced

    def cosine_single_comparison(self, query, intent):
        """Performs a cosine similarity comparison between a query and an intent
        inside self.intents. It basically computes a score base on synthactical similarity.
        """
        try:
            assert hasattr(self, 'intents')
        except:
            raise Exception('[ERROR] Intent list not defined!')
        try:
            assert intent in self.intents.index
        except:
            raise Exception('[ERROR] ({}) not defined in intent list'.format(intent))

        key = self._slice_intents([intent]).DOC.values[0]
        tfidfs = VECTORIZER.fit_transform([key, query])
        return cosine_similarity(tfidfs[0, :], tfidfs[1, :]).squeeze()

    def cosine_parse(self, query, data=None, **kwargs):
        """Decides which intent is most likely to be referred by the given query.
        Data can be optionally passed to be used instead of self.intents
        """
        try:
            assert hasattr(self, 'intents')
        except:
            raise Exception('[ERROR] Intent list not defined!')

        # add query to intent frame
        if data is None:
            query_frame = self.intents.copy()
        else:
            query_frame = data.copy()
        # cleaned = CLEANER.remove_stopwords_text(query.lower())
        cleaned = query.lower()
        new_row = pd.DataFrame({'DOC': cleaned,
                                'REGEX': ''},
                               index=['TBD'])
        query_frame = query_frame.append(new_row)

        # compute TF-IDF scores
        tfidfs = VECTORIZER.fit_transform(query_frame.DOC)

        # compute cosine similarity scores
        query_tfidf = tfidfs[-1, :]
        comps = []
        for _, vect in enumerate(tfidfs[:-1, :]):
            score = cosine_similarity(query_tfidf, vect).squeeze()
            comps.append(score)
        comps = pd.DataFrame(index=query_frame.index[:-1],
                             data={'SCORE': comps})
        comps.SCORE = comps.SCORE/sum(comps.SCORE)
        try:
            decision = comps.index[comps.SCORE == max(comps.SCORE)][0]
        except:
            return "😭", 'scores.png'
        if kwargs is not None:
            if 'serialize' in kwargs and kwargs['serialize']:
                axes = comps.astype(float).plot(kind='bar')
                fig = axes.get_figure()
                fig.tight_layout()
                fig.savefig('scores.png')
                return decision, max(comps.SCORE)
            else:
                return decision, max(comps.SCORE)
        else:
            return decision, max(comps.SCORE)

    def regex_parse(self, text, regex):
        """Finds a similarity according to a regex.
        """
        return [match.group() for match in regex.finditer(text.lower())]

    def intent_parse(self, query, intents, verbose=False, **kwargs):
        """
        Main intent parsing pipeline.
        If the given (cleaned) query has at most 3 words,
        a regex match is performed, before the cosine matching.
        """
        try:
            assert hasattr(self, 'intents')
        except:
            raise Exception('[ERROR] Intent list not defined!')

        # check if list of intents is valid
        try:
            assert intents
        except:
            raise Exception('[ERROR] Intent list must be nonempty!')
        for intent in intents:
            if intent not in self.intents.index:
                raise Exception('[ERROR] Intent {} not defined in parser object!'.format(intent))

        # build verbose function
        if verbose:
            verb = lambda s: print(s)
        else:
            verb = lambda _: None

        # slice the corresponding intent rows
        arcs = self._slice_intents(intents)

        # preprocess query
        text = remove_accents(query.lower())
        text = re.sub(r'[^\w\s]', ' ', text).split()
        text = ' '.join(text)

        if len(query.split()) <= 3:
            # perform a regex search
            verb('Attempting regex parse...')
            matches = [index
                       for index, regex
                       in arcs.REGEX.iteritems()
                       if self.regex_parse(text, regex)]
            if len(matches) == 1:
                verb('Regex parse successful!!')
                return matches[0], 1.0
            else:
                verb('Regex parse not successful!!')
                verb('Attempting cosine parse...')
                if len(intents) == 1:
                    return self.cosine_single_comparison(text, intents[0])
                else:
                    return self.cosine_parse(text, data=arcs, **kwargs)
        else:
            verb('Attempting cosine parse...')
            if len(intents) == 1:
                return self.cosine_single_comparison(text, intents[0])
            else:
                return self.cosine_parse(text, data=arcs, **kwargs)
