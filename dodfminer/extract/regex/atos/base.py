import re
import utils
import pandas as pd


class Atos:
    
    def __init__(self, file):
        fp = open(file, "r")
        self._file_name = file
        self._text = fp.read()
        fp.close()

        self._acts_str = []
        self._flags = self._regex_flags()
        self._name = self._act_name()
        self._columns = self._props_names()
        self._rules = self._prop_rules()
        self._inst_rule = self._rule_for_inst()

        self._raw_acts = self._extract_instances()
        self._acts = self._acts_props() 
        self._data_frame = self._build_dataframe()

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

    def _find_instances(self):
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
        """."""
        act = {}
        act["tipo_ato"] = self._name
        for key in self._rules:
            try:
                act[key], = self._find_props(self._rules[key], act_raw)
            except:
                act[key] = "nan"

        return act
    
    def _acts_props(self):
        """."""
        acts = []
        for raw in self._raw_acts:
            act = self._act_props(raw)
            acts.append(act)
        return acts      

    def _extract_instances(self):
        """."""
        found = self._find_instances()
        results = []
        for instance in found:
            head, body = instance
            self.acts_str.append(head+body)
            results.append(body)
            
        return results

    def _build_dataframe(self):
        """."""
        if len(self._acts) > 0:
            df = pd.DataFrame(self._acts)
            df.columns = self._columns
            return df
        return pd.DataFrame()
