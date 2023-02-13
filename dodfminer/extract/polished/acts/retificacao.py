"""Regras regex para ato de retificação."""

import os
import joblib
from dodfminer.extract.polished.acts.base import Atos


class RetificacaoComissionados(Atos):
    '''
        Classe para atos de retificação de comissionados
    '''

    def __init__(self, file, backend):
        super().__init__(file, backend)

    def _act_name(self):
        return "Retificação de Comissionados"

    @classmethod
    def _section(cls):
        return "Seção II"

    def _load_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/models/comissionados_ret.pkl'
        return joblib.load(f_path)

    def _load_seg_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/seg_models/comissionados_ret.pkl'
        return joblib.load(f_path)

    def _rule_for_inst(self):
        return r"(No Decreto de)((.|\n)*?)(^((?!matr[ií]cula).|\n))*?((.|\n)*?)LEIA-?SE: \"?(\.\.\.)?.*(\.\.\.)?\"?\."

    def _prop_rules(self):
        return {} # regex para entidades não implementado

    def get_expected_colunms(self) -> list:
        return  []

    def _props_names(self):
        return ['tipo'] + self.get_expected_colunms()

class RetificacaoEfetivos(Atos):
    '''
    Classe para atos de retificação de efetivos
    '''

    def __init__(self, file, backend):
        super().__init__(file, backend)

    def _act_name(self):
        return "Retificação de Efetivos"

    @classmethod
    def _section(cls):
        return "Seção II"

    def _load_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/models/efetivos_ret.pkl'
        return joblib.load(f_path)

    def _load_seg_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/seg_models/efetivos_ret.pkl'
        return joblib.load(f_path)

    def _rule_for_inst(self):
        return r"(Na Ordem de S|RETIFICAR)((.|\n)*?)(matricula)((.|\n)*?)LEIA-?SE: \"?(\.\.\.)?.*(\.\.\.)?\"?\."

    def _prop_rules(self):
        return {} # regex para entidades não implementado

    def get_expected_colunms(self) -> list:
        return  []

    def _props_names(self):
        return ['tipo'] + self.get_expected_colunms()