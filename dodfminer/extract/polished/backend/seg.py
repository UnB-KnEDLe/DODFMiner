"""Base class for act segmentation.

This module contains the ActSeg class, which have all that is necessary to
extract acts from a block of text.
"""

import re
from nltk import word_tokenize


class ActSeg:
    """Base class for act segmentation.

    This class encapsulate all functions, and attributes related
    to the process of segmentation of an act.

    Note:
        This class is one of the fathers of the Base act class.

    Attributes:
        _seg_function: Function for segmentation.

    """

    def __init__(self):
        self._seg_function = self._load_seg_function()

    def _load_seg_function(self):
        """Load segmentation function into the _seg_function variable.

        If the segmentation backend is ner and a NER model is available, loads the function _crf_instances.
        Otherwise, loads the function _regex_instances.

        """
        if self._backend == 'ner':
            self._seg_model = self._load_seg_model()
            if self._seg_model is not None:
                return self._crf_instances
            else:
                print(
                    f"Act {self._name} does not have a segmentation model: Using regex for segmentation")
                return self._regex_instances
        else:
            self._backend = 'regex'
            return self._regex_instances

    def _load_seg_model(self):
        """Load Segmentation Model from models/folder.

        Note:
            This function needs to be overwriten in
            the child class. If this function is not
            overwrite the segmentation backend will fall back to regex.

        """
        return None

    def _regex_instances(self):
        """Search for all instances of the act using the defined rule.

        Returns:
            List of all act instances in the text.
        """

        # pylint: disable=no-member
        found = re.findall(self._inst_rule, self._text, flags=self._flags)
        results = []
        for instance in found:
            head, body, *_ = instance
            # pylint: disable=no-member
            self._acts_str.append(head+body)
            results.append(body)

        return results

    def _crf_instances(self):
        """Search for all instances of the act using a CRF model.

        Returns:
            List of all act instances in the text.
        """
        text = self._preprocess(self._text)
        feats = self._get_features(text)
        pred = self._seg_model.predict_single(feats)
        acts = self._extract_acts(text, pred)
        self._acts_str += acts
        return acts

    def _preprocess(self, text):
        """Preprocess text for CRF model."""
        return word_tokenize(text.replace('-', ' - ').replace('/', ' / ').replace('.', ' . ').replace(',', ' , '))

    def _number_of_digits(self, s):
        """Returns number of digits in a string."""
        return sum(c.isdigit() for c in s)

    def _get_base_feat(self, word):
        """Returns basic features for a word, used in the CRF model."""
        d = {
            'word': word.lower(),
            'is_title': word.istitle(),
            'is_upper': word.isupper(),
            'num_digits': str(self._number_of_digits(word)),
        }
        return d

    def _get_features(self, text):
        """Create features for each word in a text.

        Args:
            text (list): List of words in an act.
        Returns:
            A list with a dictionary of features for each of the words.
        """
        features = []

        for i in range(len(text)):
            word = text[i]

            word_before = '' if i == 0 else text[i-1]
            word_before2 = '' if i <= 1 else text[i-2]
            word_before3 = '' if i <= 2 else text[i-3]
            word_before4 = '' if i <= 3 else text[i-4]

            word_after = '' if i+1 == len(text) else text[i+1]
            word_after2 = '' if i+2 >= len(text) else text[i+2]
            word_after3 = '' if i+3 >= len(text) else text[i+3]
            word_after4 = '' if i+4 >= len(text) else text[i+4]

            word_before = self._get_base_feat(word_before)
            word_before2 = self._get_base_feat(word_before2)
            word_before3 = self._get_base_feat(word_before3)
            word_before4 = self._get_base_feat(word_before4)
            word_after = self._get_base_feat(word_after)
            word_after2 = self._get_base_feat(word_after2)
            word_after3 = self._get_base_feat(word_after3)
            word_after4 = self._get_base_feat(word_after4)

            word_feat = {
                'bias': 1.0,
                'word': word.lower(),
                'is_title': word.istitle(),
                'is_upper': word.isupper(),
                'num_digits': str(self._number_of_digits(word)),
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

            if i > 3:
                word_feat.update({
                    '-4:word': word_before4['word'].lower(),
                    '-4:title': word_before4['is_title'],
                    '-4:upper': word_before4['is_upper'],
                    '-4:num_digits': word_before4['num_digits'],
                })

            if i < len(text) - 1:
                word_feat.update({
                    '+1:word': word_after['word'].lower(),
                    '+1:title': word_after['is_title'],
                    '+1:upper': word_after['is_upper'],
                    '+1:num_digits': word_after['num_digits'],
                })
            else:
                word_feat['EOS'] = True

            if i < len(text) - 2:
                word_feat.update({
                    '+2:word': word_after2['word'].lower(),
                    '+2:title': word_after2['is_title'],
                    '+2:upper': word_after2['is_upper'],
                    '+2:num_digits': word_after2['num_digits'],
                })

            if i < len(text) - 3:
                word_feat.update({
                    '+3:word': word_after3['word'].lower(),
                    '+3:title': word_after3['is_title'],
                    '+3:upper': word_after3['is_upper'],
                    '+3:num_digits': word_after3['num_digits'],
                })

            if i < len(text) - 4:
                word_feat.update({
                    '+4:word': word_after4['word'].lower(),
                    '+4:title': word_after4['is_title'],
                    '+4:upper': word_after4['is_upper'],
                    '+4:num_digits': word_after4['num_digits'],
                })

            features.append(word_feat)

        return features

    def _extract_acts(self, text, prediction):
        """Extract and join words predicted to be part of an act.

        Args:
            text (list): List of words in an act.
            prediction (list): Predictions made for each word in the act.

        """
        acts = []

        current_act = []
        reading_act = False
        for i in range(len(prediction)):
            if prediction[i][0] == 'B':  # B-ato
                reading_act = True
                current_act.append(text[i])
                continue

            if reading_act:
                current_act.append(text[i])

            if reading_act and prediction[i][0] == 'E':  # E-ato
                acts.append(' '.join(current_act))
                current_act = []
                reading_act = False

        if reading_act:
            acts.append(' '.join(current_act))

        return acts
