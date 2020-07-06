"""Base class for an Act model.

This module contains the Atos class, which have all that is necessary to
extract information from a specialized act.
"""

import re
import utils
import pandas as pd


class Atos:
    """Base class for extracting an act and its proprieties to a dataframe.

    Note:
        You should not use this class alone, use its childs on the regex.core module.

    Args:
        file (str): The dodf file path.

    Attributes:
        _file_name (str): The dodf file path.
        _text (str): The dodf content in string format.
        _acts_str (str): List of raw text acts.
        _flags (list): List of all flags to be used in the regex search.
        _name (str): Name of the act.
        _columns (str): List of the proprieties names from the act.
        _rules (dict): Dictionary of regex rules, one entry for each propriety.
        _inst_rule (str): Regex rule for extracting an act.
        _raw_acts (list): List of raw text acts .
        _acts (list): List of acts with propreties extracted.
        _data_frame (dataframe): The resulting dataframe from the extraction process.

    """
    
    def __init__(self, file):
        fp = open(file, "r")
        self._file_name = file
        self._text = fp.read()
        fp.close()

        self._model = self._load_model()

        self._acts_str = []
        self._flags = self._regex_flags()
        self._name = self._act_name()
        self._columns = self._props_names()
        self._rules = self._prop_rules()
        self._inst_rule = self._rule_for_inst()

        self._raw_acts = self._extract_instances()
        self._acts = self._acts_props() 
        self._data_frame = self._build_dataframe()

    def _load_model(self):
        raise NotImplementedError

    @property
    def data_frame(self):
        """:obj:`dataframe`: Act dataframe with proprieties extracted."""
        return self._data_frame

    @property
    def name(self):
        """str: Name of the act."""
        return self._name

    @property
    def acts_str(self):
        """str: Vector of acts content as raw text."""
        return self._acts_str

    def _regex_flags(self):
        """Flags of the regex search"""
        return 0

    def _act_name(self):
        """Name of the act.
        
        Must return a single string representing the act name

        Raises:
            NotImplementedError: Child class needs to overwrite this method.

        """
        raise NotImplementedError

    def _props_names(self):
        """Name of all the proprieties for the dataframe column.
        
        Must return a vector of string representing the proprieties names

        Warning:
            The first name will be used for the type-of-act propriety.

        Raises:
            NotImplementedError: Child class needs to overwrite this method.
        
        """
        raise NotImplementedError
        
    def _inst_rule(self):
        """Rule for extraction of the act
        
        Warning:
            Must return a regex rule that finds an act in two parts, containing a head
            and a body. Where only the body will be used to search for proprieties.

        Raises:
            NotImplementedError: Child class needs to overwrite this method.
 
        """
        raise NotImplementedError
    
    def _prop_rules(self):
        """Rules for extraction of the proprieties.
        
        Must return a dictionary of regex rules, where the key is the propriety type
        and the value is the rule.

        Raises:
            NotImplementedError: Child class needs to overwrite this method

        """
        raise NotImplementedError 

    def _find_instances(self, backend):
        """Search for all instances of the act using the defined rule.
        
        Returns:
            List of all act instances in the text.
        """
        return re.findall(self._inst_rule, self._text, flags=self._flags)
    
    def _find_props(self, rule, act):
        """Find a single proprietie in an single act.

        Args:
            rule (str): The regex rule to search for.
            act (str): The act to apply the rule.

        Returns: 
            The found propriety, or a nan in case nothing is found.

        """
        match = re.search(rule, act, flags=self._flags) 
        if match:
            return tuple(x for x in match.groups() if x != None)
        return "nan"
    
    def _act_props(self, act_raw):
        """Create an act dict with all its proprieties.
        
        Args:
            act_raw (str): The raw text of a single act.

        Returns:
            The act, and its props in a dictionary format.

        """
        act = {}
        act["tipo_ato"] = self._name
        for key in self._rules:
            try:
                act[key], = self._find_props(self._rules[key], act_raw)
            except:
                act[key] = "nan"

        return act
    
    def _acts_props(self):
        """Extract proprieties of all the acts.
    
        Returns:
            A vector of extracted acts dictionaries.
        """
        acts = []
        for raw in self._raw_acts:
            act = self._act_props(raw)
            acts.append(act)
        return acts      

    def _extract_instances(self):
        """Extract instances of an act.

        Warning:
            Instance must have an head and an body.

        Returns:
            All the instances of the act found.

        """
        found = self._find_instances()
        results = []
        for instance in found:
            head, body = instance
            self.acts_str.append(head+body)
            results.append(body)
            
        return results

    def _build_dataframe(self):
        """Create a dataframe with the extracted proprieties.

        Returns:
            The dataframe created
        """
        if len(self._acts) > 0:
            df = pd.DataFrame(self._acts)
            df.columns = self._columns
            return df
        return pd.DataFrame()


    ######## NEW STUFF

    # def __init__(self, model_path):
        # Load trained NER model
        self.model = joblib.load(model_path)

    def get_features(self, sentence):
        sent_features = []
        for i in range(len(sentence)):
            word_feat = {
                'word': sentence[i].lower(),
                'capital_letter': sentence[i][0].isupper(),
                'all_capital': sentence[i].isupper(),
                'isdigit': sentence[i].isdigit(),
                'word_before': sentence[i].lower() if i==0 else sentence[i-1].lower(),
                'word_after:': sentence[i].lower() if i+1>=len(sentence) else sentence[i+1].lower(),
                'BOS': i==0,
                'EOS': i==len(sentence)-1
            }
            sent_features.append(word_feat)
        return sent_features

    def prediction(self, sentence):
        if isinstance(sentence[0], list):
            feats = []
            for i in range(len(sentence)):
                feats.append(self.get_features(sentence[i]))
            predictions = self.model.predict(feats)
            return predictions
        else:
            feats = self.get_features(sentence)
            predictions = self.model.predict_single(feats)
            return self.dataFramefy(sentence, predictions)
            print("DFfy")
        # return predictions

    # TODO create dataframe with identified entities
    def dataFramefy(self, sentence, prediction):
        # Create dictionary of tags to save predicted entities
        tags = self.model.classes_
        tags.remove('O')
        tags.sort(reverse=True)
        while(tags[0][0] == 'I'):
            del tags[0]
        for i in range(len(tags)):
            tags[i] = tags[i][2:]
        dict = {}
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
            tags[last_tag[2:]].append(temp_entity)

        return dict
