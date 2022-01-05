"""NER backend for act and propriety extraction.

This module contains the ActNER class, which have all that is necessary to
extract an act and, its proprieties, using a trained ner model.

"""

import os
import nltk
import numpy as np
import joblib
from nltk import word_tokenize

# pylint: disable=too-few-public-methods


class ActNER:
    """Act NER Class.

    This class encapsulate all functions, and attributes related
    to the process of NER extraction.

    Note:
        This class is one of the fathers of the Base act class.

    Attributes:
        _model: The trained NER model for the act

    """

    def __init__(self):
        # self._backend = 'regex'
        nltk.download('punkt', quiet=True)
        super().__init__()

        # pylint: disable=assignment-from-no-return
        self._model = self._load_model()

    def _load_model(self):
        """Load Model from models/folder.

        Note:
            This function needs to be overwriten in
            the child class. If this function is not
            overwrite the backend will fall back to regex.

        """
        # pylint: disable=access-member-before-definition
        if self._backend == 'ner':
            print(
                f"Act {self._name} does not have a model: FALLING BACK TO REGEX")
            self._backend = 'regex'
        else:
            self._backend = 'regex'

    @classmethod
    def number_of_digits(self, s):
        """ Returns number of digits in string. """
        return sum(c.isdigit() for c in s)

    @classmethod
    def get_base_feat(self, word):
        """ Returns base features of a word. """
        d = {
            'word': word.lower(),
            'is_title': word.istitle(),
            'is_upper': word.isupper(),
            'num_digits': str(self.number_of_digits(word)),
        }
        return d

    @classmethod
    def _get_features(cls, sentence):
        """Create features for each word in act.

        Create a list of dict of words features to be used in the predictor module.

        Args:
            act (list): List of words in an act.

        Returns:
            A list with a dictionary of features for each of the words.

        """
        sent_features = []

        for i in range(len(sentence)):
            word = sentence[i]

            word_before = '' if i == 0 else sentence[i-1]
            word_before2 = '' if i <= 1 else sentence[i-2]
            word_before3 = '' if i <= 2 else sentence[i-3]

            word_after = '' if i+1 == len(sentence) else sentence[i+1]
            word_after2 = '' if i+2 >= len(sentence) else sentence[i+2]
            word_after3 = '' if i+3 >= len(sentence) else sentence[i+3]

            word_before = cls.get_base_feat(word_before)
            word_before2 = cls.get_base_feat(word_before2)
            word_before3 = cls.get_base_feat(word_before3)
            word_after = cls.get_base_feat(word_after)
            word_after2 = cls.get_base_feat(word_after2)
            word_after3 = cls.get_base_feat(word_after3)

            word_feat = {
                'bias': 1.0,
                'word': word.lower(),
                'is_title': word.istitle(),
                'is_upper': word.isupper(),
                'is_digit': word.isdigit(),

                'num_digits': str(cls.number_of_digits(word)),
                'has_hyphen': '-' in word,
                'has_dot': '.' in word,
                'has_slash': '/' in word,
            }

            if i > 0:
                word_feat.update({
                    '-1:word': word_before['word'].lower(),
                    '-1:title': word_before['is_title'],
                    '-1:upper': word_before['is_upper'],
                    '-1:num_digits': word_before['num_digits'],
                })
            else:
                word_feat['BOS'] = True

            if i > 1:
                word_feat.update({
                    '-2:word': word_before2['word'].lower(),
                    '-2:title': word_before2['is_title'],
                    '-2:upper': word_before2['is_upper'],
                    '-2:num_digits': word_before2['num_digits'],
                })

            if i > 2:
                word_feat.update({
                    '-3:word': word_before3['word'].lower(),
                    '-3:title': word_before3['is_title'],
                    '-3:upper': word_before3['is_upper'],
                    '-3:num_digits': word_before3['num_digits'],
                })

            if i < len(sentence) - 1:
                word_feat.update({
                    '+1:word': word_after['word'].lower(),
                    '+1:title': word_after['is_title'],
                    '+1:upper': word_after['is_upper'],
                    '+1:num_digits': word_after['num_digits'],
                })
            else:
                word_feat['EOS'] = True

            if i < len(sentence) - 2:
                word_feat.update({
                    '+2:word': word_after2['word'].lower(),
                    '+2:title': word_after2['is_title'],
                    '+2:upper': word_after2['is_upper'],
                    '+2:num_digits': word_after2['num_digits'],
                })

            if i < len(sentence) - 3:
                word_feat.update({
                    '+3:word': word_after3['word'].lower(),
                    '+3:title': word_after3['is_title'],
                    '+3:upper': word_after3['is_upper'],
                    '+3:num_digits': word_after3['num_digits'],
                })

            sent_features.append(word_feat)

        return sent_features

    def add_common_attributes(self, feats):
        f_path = os.path.dirname(os.path.dirname(__file__))
        f_path += '/acts/models/atributos_gerais.pkl'
        crf = joblib.load(f_path)

        predictions = crf.predict_single(feats)

        for i in range(len(feats)):
            feats[i]['predicao'] = predictions[i]

    def _prediction(self, act):
        """Predict classes for a single act.

        Args:
            act (string): Full act

        Returns:
            A dictionary with the proprieties and its
            predicted value.
        """
        print("Predicting")
        act = self._preprocess(act)

        feats = self._get_features(act)
        self.add_common_attributes(feats)

        predictions = self._model.predict_single(feats)
        return self._predictions_dict(act, predictions)

    @classmethod
    def _preprocess(cls, sentence):
        """Transform a raw string to a list of words.

        Args:
            sentence (string): Raw act as string.

        Returns:
            The list of words in the act.
        """
        sentence = word_tokenize(sentence.replace(
            '/', ' / ').replace(':', ' : ').replace('``', ' ').replace("''", ' '))
        return sentence

    def _predictions_dict(self, sentence, prediction):
        """Create dictionary of proprieties.

        Create dictionary of tags to save predicted entities.

        Args:
            sentence (list): List of words and tokens in the act.
            prediction ([type]): The correspondent predicitons for each
                                 word in the sentence.

        Returns:
            A dictionary of the proprieties found.

        """
        tags = self._model.classes_
        tags.remove('O')
        tags.sort(reverse=True)
        while tags[0][0] == 'I':
            del tags[0]
        for i, _ in enumerate(tags):
            tags[i] = tags[i][2:]
        dict_ato = {}
        dict_ato["Tipo do Ato"] = ""
        for i in tags:
            dict_ato[i] = []

        last_tag = 'O'
        temp_entity = []
        for i, _ in enumerate(prediction):
            if last_tag not in (prediction[i], 'O'):
                dict_ato[last_tag[2:]].append(temp_entity)
                temp_entity = []
            if prediction[i] == 'O':
                last_tag = 'O'
                continue
            # else:
            temp_entity.append(sentence[i])
            last_tag = "I" + prediction[i][1:]

        if temp_entity:
            dict_ato[last_tag[2:]].append(temp_entity)

        for key, ato in dict_ato.items():
            values = []
            for value in ato:
                value = ' '.join(value)
                values.append(value)
            if len(values) >= 1:
                dict_ato[key] = values[0]

            if dict_ato[key] == []:
                dict_ato[key] = np.nan

        # pylint: disable=no-member
        dict_ato["Tipo do Ato"] = self._name

        return dict_ato
