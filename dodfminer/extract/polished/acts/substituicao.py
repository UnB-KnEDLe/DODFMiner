"""Regras regex para ato de Substituição."""

import re
import os
import joblib
from dodfminer.extract.polished.acts.base import Atos


class Substituicao(Atos):
    '''
    Classe para atos de substituição
    '''

    def __init__(self, file, backend):
        super().__init__(file, backend)

    # def _load_model(self):
    #     f_path = os.path.dirname(__file__)
    #     f_path += '/models/substituicao_ner.pkl'
    #     return joblib.load(f_path)

    def _regex_flags(self):
        return re.IGNORECASE

    def _load_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/models/substituicao.pkl'
        return joblib.load(f_path)

    def _load_seg_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/seg_models/substituicao.pkl'
        return joblib.load(f_path)

    def _act_name(self):
        return "Substituição de Funções"

    def get_expected_colunms(self) -> list:
        return [
            'Nome_substituto',
            'Cargo_substituto',
            'Matricula_substituto',
            'Nome_substituido',
            'Matricula_substituido',
            'Simbolo_substituto',
            'Cargo_objeto_substituicao',
            'Simbolo_objeto_substituicao',
            'Hierarquia_lotacao',
            'Orgao',
            'Data_inicial',
            'Data_final',
            'Matricula_siape',
            'Motivo',
        ]

    def _props_names(self):
        return ["Tipo do Ato"] + self.get_expected_colunms()

    def _rule_for_inst(self):
        start = r"(DESIGNAR)"
        body = r"([\s\S]*?)"
        end = r"\.\s"
        return start + body + end

    def _prop_rules(self):

        rules = {
            "nome_substituto": r"(^[A-ZÀ-Ž\s]+[A-ZÀ-Ž])",
            "matricula_substituto": r"(?:^[A-ZÀ-Ž\s]+[A-ZÀ-Ž])\s[\s\S]*?\smatr[í|i]cula\s?n?o?\s([\s\S]*?)[,|\s]",
            "nome_substituido": r"para\ssubstituir\s([A-ZÀ-Ž\s]+[A-ZÀ-Ž])",
            "matricula_substituido": r"matr[í|i]cula\s?n?o?\s(?:[\s\S]*?)[\s\S]*?matr[í|i]cula\s?n?o?\s([\s\S]*?),",
            "cargo_substituto": r"para\ssubstituir\s(?:[A-ZÀ-Ž\s]+[A-ZÀ-Ž]),\smatr[í|i]cula\s?n?o?\s(?:[\s\S]*?),\s([\s\S]*?),",
            "simbolo_substituto": r"[S|s][í|i]mbolo\s?n?o?\s([\s\S]*?)[,|\s]",
            "cargo_objeto_substituicao": "",
            "simbolo_objeto_substituicao": r"[S|s][í|i]mbolo\s?n?o?\s(?:[\s\S]*?)[\s\S]*?[S|s][í|i]mbolo\s?n?o?\s([\s\S]*?)",
            "hierarquia_lotacao": "",
            "orgao": r"(?:[S|s][í|i]mbolo\s?n?o?\s(?:[\s\S]*?)[,|\s])\sde(?:[\s\S]*?),\sd[a|e|o]\s(?:[\s\S]*,?),\sd[a|e|o]\s([\s\S]*?)$",
            "data_inicial": "",
            "data_final": "",
            "matricula_SIAPE": r"[S|s][I|i][A|a][P|p][E|e]\s[N|n]?[o|O]?\s([\s\S]*?)[,| | .]",
            "motivo": r''
        }
        return rules
