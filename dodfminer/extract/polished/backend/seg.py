"""Base class for act segmentation.

This module contains the ActSeg class, which have all that is necessary to
extract acts from a block of text.
"""

import re


class ActSeg: # pylint: disable=too-few-public-methods
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
        if self._backend == 'ner': # pylint: disable=access-member-before-definition
            self._seg_model = self._load_seg_model() # pylint: disable=assignment-from-none

            if self._seg_model is not None:
                return self._crf_instances

            print(
                f"Act {self._name} does not have a segmentation model: FALLING BACK TO REGEX")
            return self._regex_instances

        self._backend = 'regex'
        return self._regex_instances

    #pylint: disable=no-self-use
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
            self._acts_str.append(head+body)
            results.append(body)

        return results

    def _crf_instances(self):
        """Search for all instances of the act using a CRF model.

        Returns:
            List of all act instances in the text.
        """
        text = self._preprocess(self._text) # pylint: disable=no-member
        feats = self._get_features(self._split_sentence(text))
        pred = self._seg_model.predict_single(feats)
        acts = self._extract_acts(text, pred)
        self._acts_str += acts # pylint: disable=no-member
        return acts

    def _preprocess(self, text):
        """Preprocess text for CRF model."""
        return text.replace('\n', ' ').strip()

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

    def _get_base_feat(self, word):
        """Get the base features of a word, for the CRF model.

        Args:
            word (str): Word to be processed.

        Returns:
            Dictionary with the base features of the word.
        """
        feature_dict = {
            'word': word.lower(),
            'is_title': word.istitle(),
            'is_upper': word.isupper(),
            'num_digits': str(sum(c.isdigit() for c in word)),
        }
        return feature_dict

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
            for feat, _ in word_feat.items():
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

    def _extract_acts(self, text, prediction):
        """Extract and join words predicted to be part of an act.

        Args:
            text (list): List of words in the text of a DODF.
            prediction (list): Predictions made for each word in the text.

        Returns:
            List of acts in the text.
        """

        acts = []
        limits = self._limits(text)

        limits.append(len(text))
        prediction.append('O')

        act_start = -1
        # we start at 1 because sometimes the first word is tagged incorrectly
        for i in range(1, len(prediction)):
            if prediction[i][0] == 'B':  # B-act
                act_start = limits[i]
            elif prediction[i][0] == 'E' and act_start != -1:  # E-act
                act_end = limits[i+1]

                act = text[act_start:act_end].strip()
                if act.count('.') <= len(act)/3:
                    acts.append(act)
                act_start = -1

        if act_start != -1:
            acts.append(text[act_start:].strip())

        return acts
