"""NER backend for act and propriety extraction.

This module contains the ActNER class, which have all that is necessary to
extract an act and, its proprieties, using a trained ner model.

"""

import numpy as np
import os
import joblib
import re

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
            print(f"Act {self._name} does not have a model: FALLING BACK TO REGEX")
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

    def _limits(self, sentence):
        """Find the limits of words in the sentence.
        
        Args:
            sentence (str): target sentence.
            
        Returns:
            List of the positions in which each word in sentence starts.
        """
        letters = [chr(c) for c in range(ord('a'), ord('z') + 1)]
        numbers = [chr(c) for c in range(ord('0'), ord('9') + 1)]
        symbols = ['(', ',', '.', '/', '-']
        all = letters + numbers + symbols + [' ']

        # print(sentence)

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
            elif current not in all and previous in letters:
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

    def _get_base_feat(self, word):
        """Get the base features of a word, for the CRF model.
        
        Args:
            word (str): Word to be processed.
            
        Returns:
            Dictionary with the base features of the word.
        """
        d = {
            'word': word.lower(),
            'is_title': word.istitle(),
            'is_upper': word.isupper(),
            'num_digits': str(sum(c.isdigit() for c in word)),
        }
        return d

    def _add_base_feat(self, features, sentence, index, prefix):
        """Updates a dictionary of features with the features of a word.
        
        Args:
            features (dict): Dictionary with the features already processed.
            sentence (list): List of words in the sentence.
            index (int): Index of the current word in the sentence. 
            prefix (str): Prefix to be added to the name of the features of the current word.

        """
        if index >= 0 and index < len(sentence):
            word_feat = self._get_base_feat(sentence[index])
            for feat in word_feat.keys():
                features[prefix + feat] = word_feat[feat]

    def _get_features(self, sentence):
        """Get the features of a sentence, for the CRF model.
        
        Args:
            sentence (list): List of words in the sentence.
            
        Returns:
            List of dictionaries with the features of each word.
        """
        sent_features = []
        
        for i in range(len(sentence)):
            word = sentence[i]

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
        for c in self._model.classes_:
            if c == 'O':
                continue
            dict_ato[c[2:]] = []
            
        limits = self._limits(sentence)
        
        limits.append(len(sentence))
        prediction.append('O')

        current = ''
        entity_start = -1
        for i in range(len(prediction)):
            if current != '' and prediction[i] != 'I-' + current:
                entity_end = limits[i]
                dict_ato[current].append(sentence[entity_start:entity_end].strip())
                entity_start = -1
                current = ''

            if prediction[i][0] == 'B' or (prediction[i][0] == 'I' and current == ''):
                current = prediction[i][2:]
                entity_start = limits[i]

        for i in dict_ato.keys():
            if len(dict_ato[i]) == 0:
                dict_ato[i] = np.nan
            elif len(dict_ato[i]) == 1:
                dict_ato[i] = dict_ato[i][0]


        return dict_ato
