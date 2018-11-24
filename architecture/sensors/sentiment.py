#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pandas as pd
import tensorflow as tf
import tensorflow_hub as hub

MODEL_PATH = 'models/sentiment-classif'

print('Loading tf model...')

embedded_text_feature_column = hub.text_embedding_column(
    key="sentence", 
    module_spec="https://tfhub.dev/google/nnlm-en-dim128/1")

estimator = tf.estimator.DNNClassifier(
    hidden_units=[500, 100],
    feature_columns=[embedded_text_feature_column],
    model_dir=MODEL_PATH)

print('Done!')

def predict_sentiment(sentence):
    sample_df = pd.DataFrame({'sentence': [sentence]})
    sample_fn = tf.estimator.inputs.pandas_input_fn(sample_df, shuffle=False)
    for pred in estimator.predict(sample_fn):
        classif = pred['class_ids']
        return classif
    return None