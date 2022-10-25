"""NER backend for act and propriety extraction.

This module contains the ActNER class, which have all that is necessary to
extract an act and, its proprieties, using a trained ner model.

"""

import re
import nltk
import numpy as np

# pylint: disable=too-few-public-methods

class JsonNER:
    @staticmethod
    def __get_features(sentence):
        sent_features = []
        for i in range(len(sentence)):
            word_feat = {
                # Palavra atual
                'word': sentence[i].lower(),
                'capital_letter': sentence[i][0].isupper(),
                'all_capital': sentence[i].isupper(),
                'isdigit': sentence[i].isdigit(),
                # Uma palavra antes
                'word_before': '' if i == 0 else sentence[i-1].lower(),
                'word_before_isdigit': '' if i == 0 else sentence[i-1].isdigit(),
                'word_before_isupper': '' if i == 0 else sentence[i-1].isupper(),
                'word_before_istitle': '' if i == 0 else sentence[i-1].istitle(),
                # Uma palavra depois
                'word_after': '' if i+1 >= len(sentence) else sentence[i+1].lower(),
                'word_after_isdigit': '' if i+1 >= len(sentence) else sentence[i+1].isdigit(),
                'word_after_isupper': '' if i+1 >= len(sentence) else sentence[i+1].isupper(),
                'word_after_istitle': '' if i+1 >= len(sentence) else sentence[i+1].istitle(),

                'BOS': i == 0,
                'EOS': i == len(sentence)-1
            }
            sent_features.append(word_feat)
        return sent_features
    
    @staticmethod
    def predict(sentence, model):
        # word_tokenize
        text = nltk.tokenize.word_tokenize(sentence)
        # get_features
        sent_features = JsonNER.__get_features(text)
        # crf precisa de um input em formato de lista mesmo que contenha só um elemento
        # e também retorna a predição em formato de lista
        # por isso ([sent_features])[0], pois faremos a predição de um ato por vez
        return model.predict([sent_features])[0]


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
                f"Act {self._name} does not have an entity extraction model: FALLING BACK TO REGEX")
            self._backend = 'regex'
        else:
            self._backend = 'regex'

    def _prediction(self, act):
        """Predict classes for a single act.

        Args:
            act (string): Full act

        Returns:
            A dictionary with the proprieties and its
            predicted value.
        """
        act = self._preprocess(act)
        feats = self._get_features(self._split_sentence(act))
        pred = self._model.predict_single(feats)
        return self._predictions_dict(act, pred)

    @classmethod
    def _preprocess(cls, text):
        """Preprocess text for CRF model."""
        text = text.replace('\n', ' ').strip()
        text = re.sub(' +', ' ', text)
        text = re.sub(r'([a-zA-Z0-9])- ', r'\1', text)
        return text

    @classmethod
    def _limits(cls, sentence):
        """Find the limits of words in the sentence.

        Args:
            sentence (str): target sentence.

        Returns:
            List of the positions in which each word in sentence starts.
        """
        letters = [chr(c) for c in range(ord('a'), ord('z') + 1)]
        numbers = [chr(c) for c in range(ord('0'), ord('9') + 1)]
        symbols = ['(', ',', '.', '/', '-']
        all_chars = letters + numbers + symbols + [' ']

        lim = []
        if sentence[0] != ' ':
            lim.append(0)

        for i in range(1, len(sentence)):
            current = sentence[i].lower()
            previous = sentence[i-1].lower()

            if current in letters and previous not in letters:
                lim.append(i)
            elif current in numbers and previous not in numbers:
                lim.append(i)
            elif current in symbols:
                lim.append(i)
            elif current not in all_chars and previous in letters:
                lim.append(i)
        return lim

    def _split_sentence(self, sentence):
        """Split a sentence into words.

        Args:
            sentence (str): Sentence to be split.

        Returns:
            List of words in the sentence.
        """
        lim = self._limits(sentence)
        lim.append(len(sentence))

        words = []
        for i in range(1, len(lim)):
            words.append(sentence[lim[i-1]:lim[i]].strip())
        return words

    @classmethod
    def _get_base_feat(cls, word):
        """Get the base features of a word, for the CRF model.

        Args:
            word (str): Word to be processed.

        Returns:
            Dictionary with the base features of the word.
        """
        features_dict = {
            'word': word.lower(),
            'is_title': word.istitle(),
            'is_upper': word.isupper(),
            'num_digits': str(sum(c.isdigit() for c in word)),
        }
        return features_dict

    def _add_base_feat(self, features, sentence, index, prefix):
        """Updates a dictionary of features with the features of a word.

        Args:
            features (dict): Dictionary with the features already processed.
            sentence (list): List of words in the sentence.
            index (int): Index of the current word in the sentence.
            prefix (str): Prefix to be added to the name of the features of the current word.

        """
        if 0 <= index < len(sentence):
            word_feat = self._get_base_feat(sentence[index])
            for feat,_ in word_feat.items():
                features[prefix + feat] = word_feat[feat]

    def _get_features(self, sentence):
        """Get the features of a sentence, for the CRF model.

        Args:
            sentence (list): List of words in the sentence.

        Returns:
            List of dictionaries with the features of each word.
        """
        sent_features = []

        for i,_ in enumerate(sentence):

            word_feat = {
                'bias': 1.0,
                'text_position': i/len(sentence),
            }

            self._add_base_feat(word_feat, sentence, i-4, '-4:')
            self._add_base_feat(word_feat, sentence, i-3, '-3:')
            self._add_base_feat(word_feat, sentence, i-2, '-2:')
            self._add_base_feat(word_feat, sentence, i-1, '-1:')

            self._add_base_feat(word_feat, sentence, i, '')

            self._add_base_feat(word_feat, sentence, i+1, '+1:')
            self._add_base_feat(word_feat, sentence, i+2, '+2:')
            self._add_base_feat(word_feat, sentence, i+3, '+3:')
            self._add_base_feat(word_feat, sentence, i+4, '+4:')

            sent_features.append(word_feat)

        return sent_features

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

        dict_ato = {}
        for klass in self._model.classes_:
            if klass == 'O':
                continue
            dict_ato[klass[2:]] = []

        limits = self._limits(sentence)

        limits.append(len(sentence))
        prediction.append('O')

        current = ''
        entity_start = -1
        for i,_ in enumerate(prediction):
            if current != '' and prediction[i] != 'I-' + current:
                entity_end = limits[i]
                dict_ato[current].append(
                    sentence[entity_start:entity_end].strip())
                entity_start = -1
                current = ''

            if prediction[i][0] == 'B' or (prediction[i][0] == 'I' and current == ''):
                current = prediction[i][2:]
                entity_start = limits[i]

        for key, val in dict_ato.items():
            if len(val) == 0:
                dict_ato[key] = np.nan
            elif len(val) == 1:
                dict_ato[key] = val[0]

        return dict_ato
