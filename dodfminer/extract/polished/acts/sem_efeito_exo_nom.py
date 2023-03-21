import re
import os
from typing import List, Match
import joblib
from dodfminer.extract.polished.acts.base import Atos

class SemEfeitoExoNom(Atos):
    '''
        Classe para atos de sem efeito exoneração/nomeação
    '''

    def __init__(self, file, backend, pipeline = None):
        super().__init__(file, backend = backend, pipeline = pipeline)

    def _act_name(self):
        return "Sem Efeito Exoneração/Nomeação"

    @classmethod
    def _section(cls):
        return "Seção II"

    def _load_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/models/sem_efeito_exo_nom.pkl'
        return joblib.load(f_path)

    def _load_seg_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/seg_models/sem_efeito_exo_nom.pkl'
        return joblib.load(f_path)

    def _rule_for_inst(self):
        return r"TORNAR(\s+)SEM(\s+)EFEITO" + r"([^\n]+\n){0,10}?[^\n]*?" + r"exonerou|nomeou"

    def _prop_rules(self):
        return {} # regex para entidades não implementado

    def get_expected_colunms(self) -> list:
        return  []

    def _props_names(self):
        return ['tipo'] + self.get_expected_colunms()