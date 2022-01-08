"""Committee Classification Class.

This module contains the Committee class, with all the necessary
functions for preprocessing and classification with a committee
of classifiers.
"""

import nltk
import numpy as np
import joblib

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer


class Committee:
    """Committee class.

    Creates a pipeline for preprocessing and classification when initialized.

    Args:
        path (str): The path to the models file.

    The models file needs to contain a list of classifiers and an object
    with the transform function to be used as embedding.
    """

    def __init__(self, path):
        self.pipe = make_pipeline(FunctionTransformer(self.remove_not_words),
                                  FunctionTransformer(self.embedding),
                                  FunctionTransformer(self.predict),
                                  FunctionTransformer(self.get_new_labels))

        nltk.download('punkt', quiet=True)
        nltk.download('rslp', quiet=True)
        nltk.download('stopwords', quiet=True)

        self.stopwords = nltk.corpus.stopwords.words('portuguese')
        self.stemmer = nltk.stem.RSLPStemmer()

        self.load_models(path)

    def load_models(self, path):
        """ Loads a list of classifiers and the object used for embedding from the specified path. """
        with open(path, 'rb') as file:
            self.clfs = joblib.load(file)
            self.vectorizer = joblib.load(file)
            self.vectorizer.tokenizer = self.tokenize

    def transform(self, X, y):
        """ Initializes the pipeline for preprocessing and classification. """
        self.y = y

        if len(y) == 0:
            return []

        return self.pipe.transform(X)

    def tokenize(self, text):
        """ Used by the vectorizer to tokenize text. """
        tokens = [word.lower()
                  for word in nltk.word_tokenize(text) if len(word) > 1]
        return [self.stemmer.stem(item) for item in tokens if item not in self.stopwords]

    def remove_not_words(self, text):
        """ Removes everything that is not a word from a text. """
        return text.str.replace(r'\w*\d\w*|\W', ' ', regex=True).str.lower()

    def embedding(self, text):
        """ Transforms the data with an embedding function. """
        return self.vectorizer.transform(text)

    def predict(self, text):
        """ Generates classifiers predictions for the data. """
        results = []
        for clf in self.clfs:
            predicted = clf.predict(text)
            results.append(predicted)

        return np.array(results).T

    def get_new_labels(self, results):
        """ Uses a committee to decide new labels from the classifiers predictions.

        If the committee does not agree on any label for an act,
        the original label is maintained.
        """
        new_types = []
        for i in range(0, len(results)):
            d = dict(zip(*np.unique(results[i], return_counts=True)))
            r = max(d, key=d.get)
            if d[r] >= 0.5 and r != self.y[i]:
                new_types.append(r)
            else:
                new_types.append(self.y[i])
        return new_types
