#coding=utf8

import string
import spacy
from spacy.lang.en import English

from sklearn.base import TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline


nlp = spacy.load('en_core_web_sm')
parser = English()


def spacy_tokenizer(sentence):
    stop_words = spacy.lang.en.stop_words.STOP_WORDS
    doc = parser(sentence)

    doc = [word.lemma_.lower().strip() 
           if word.lemma_ != "-PRON-" else word.lower_ 
           for word in doc ]

    doc = [word for word in doc 
           if word not in stop_words 
           and word not in string.punctuation]

    return doc


# class TextCleaner(TransformerMixin):
class predictors(TransformerMixin):
    def transform(self, X, **transform_params):
        return [clean_text(text) for text in X]

    def fit(self, X, y=None, **fit_params):
        return self

    def get_params(self, deep=True):
        return {}


def clean_text(text):
    return text.strip().lower()


