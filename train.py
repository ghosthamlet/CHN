#coding=utf8

import string
import spacy
from spacy.lang.en import English

from sklearn.base import TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline


# this did not load any external model, even en_core_web_sm
_nlp = English()
# _nlp = spacy.load('en_core_web_sm')
# too slow
# _nlp = spacy.load('en_core_web_md')


def spacy_tokenizer(sentence):
    stop_words = spacy.lang.en.stop_words.STOP_WORDS
    doc = _nlp(sentence)

    doc = [w.lemma_.lower().strip() 
           if w.lemma_ != "-PRON-" else w.lower_ 
           for w in doc]

    doc = [w for w in doc 
           if w not in stop_words 
           and w not in string.punctuation]

    return doc


class TextCleaner(TransformerMixin):
    def transform(self, X, **transform_params):
        return [clean_text(text) for text in X]

    def fit(self, X, y=None, **fit_params):
        return self

    def get_params(self, deep=True):
        return {}


def clean_text(text):
    return text.strip().lower()


