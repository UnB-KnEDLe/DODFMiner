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
        return self._data_frame

    @property
    def name(self):
        return self._name

    @property
    def acts_str(self):
        return self._acts_str

    def _regex_flags(self):
        return 0

    def _act_name(self):
        raise NotImplementedError

    def _props_names():
        raise NotImplementedError
        
    def _inst_rule(self):
        raise NotImplementedError
    
    def _prop_rules(self):
        raise NotImplementedError 

    def _find_instances(self):
        return re.findall(self._inst_rule, self._text, flags=self._flags)
    
    def _find_props(self, rule, act):
        match = re.search(rule, act, flags=self._flags) 
        if match:
            return match.groups()
        return "nan"
    
    def _act_props(self, act_raw):
        act = {}
        act["tipo_ato"] = self._name
        for key in self._rules:
            try:
                act[key], = self._find_props(self._rules[key], act_raw)
            except:
                act[key] = "nan"

        return act
    
    def _acts_props(self):
        acts = []
        for raw in self._raw_acts:
            act = self._act_props(raw)
            acts.append(act)
        return acts      

    def _extract_instances(self):
        found = self._find_instances()
        results = []
        for instance in found:
            head, body = instance
            self.acts_str.append(head+body)
            results.append(body)
            
        return results

    def _build_dataframe(self):
        if len(self._acts) > 0:
            df = pd.DataFrame(self._acts)
            df.columns = self._columns
            return df
        return pd.DataFrame()
