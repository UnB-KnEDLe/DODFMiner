"""NER backend for act and propriety extraction.

This module contains the ActNER class, which have all that is necessary to
extract an act and, its proprieties, using a trained ner model.

"""

import numpy as np

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
        super(ActNER, self).__init__()
        self._model = self._load_model()

    def _load_model(self):
        """Load Model from models/folder.

        Note:
            This function needs to be overwriten in
            the child class. If this function is not
            overwrite the backend will fall back to regex.

        """
        if self._backend == 'ner':
            print(f"Act {self._name} does not have an model: FALLING BACK TO REGEX")
            self._backend = 'regex'
        else:
            self._backend = 'regex'

    def _get_features(self, act):
        """Create features for each word in act.

        Create a list of dict of words features to be used in the predictor module.

        Args:
            act (list): List of words in an act.

        Returns:
            A list with a dictionary of features for each of the words.

        """
        sent_features = []
        for i in range(len(act)):
            word_feat = {
                'word': act[i].lower(),
                'capital_letter': act[i][0].isupper(),
                'all_capital': act[i].isupper(),
                'isdigit': act[i].isdigit(),
                'word_before': act[i].lower() if i == 0 else act[i-1].lower(),
                'word_after:': act[i].lower() if i+1 >= len(act) else act[i+1].lower(),
                'BOS': i == 0,
                'EOS': i == len(act)-1
            }
            sent_features.append(word_feat)
        return sent_features

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
        predictions = self._model.predict_single(feats)
        return self._predictions_dict(act, predictions)

    def _preprocess(self, sentence):
        """Transform a raw string to a list of words.

        Args:
            sentence (string): Raw act as string.

        Returns:
            The list of words in the act.
        """
        sentence = sentence.replace(',', ' , ').replace(';', ' ; '). \
                   replace(':', ' : ').replace('. ', ' . ').replace('\n', ' ')
        if sentence[len(sentence)-2:] == '. ':
            sentence = sentence[:len(sentence)-2] + " ."
        return sentence.split()

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
        while(tags[0][0] == 'I'):
            del tags[0]
        for i in range(len(tags)):
            tags[i] = tags[i][2:]
        dict = {}
        dict["Tipo do Ato"] = ""
        for i in tags:
            dict[i] = []

        last_tag = 'O'
        temp_entity = []
        for i in range(len(prediction)):
            if prediction[i] != last_tag and last_tag != 'O':
                dict[last_tag[2:]].append(temp_entity)
                temp_entity = []
            if prediction[i] == 'O':
                last_tag = 'O'
                continue
            else:
                temp_entity.append(sentence[i])
                last_tag = "I" + prediction[i][1:]

        if temp_entity:
            dict[last_tag[2:]].append(temp_entity)

        for key in dict.keys():
            values = []
            for value in dict[key]:
                value = ' '.join(value)
                values.append(value)
            if len(values) == 1:
                dict[key] = values[0]
            else:
                dict[key] = values


            if dict[key] == []:
                dict[key] = np.nan

        dict["Tipo do Ato"] = self._name


        return dict
