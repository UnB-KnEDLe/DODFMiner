"""Regras regex para atos de Reversões."""

import re
import os
import joblib
from dodfminer.extract.polished.acts.base import Atos


class Revertions(Atos):
    '''
        Classe com atos de reversão
    '''

    def __init__(self, text, backend):
        super().__init__(text, backend)

    def _regex_flags(self):
        return re.IGNORECASE

    def _act_name(self):
        return "Reversão"

    def _load_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/models/reversao.pkl'
        return joblib.load(f_path)

    def _load_seg_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/seg_models/reversao.pkl'
        return joblib.load(f_path)

    def get_expected_colunms(self) -> list:
        return [
            'Processo_sei',
            'Nome',
            'Matricula',
            'Cargo_efetivo',
            'Classe',
            'Padrao',
            'Quadro',
            'Fundamento_legal',
            'Orgao',
            'Vigencia',
        ]

    def _props_names(self):
        return [
            "Tipo do Ato",
            "Processo_sei",
            "Nome",
            "Matricula",
            "Cargo_efetivo",
            "Classe",
            "Padrao",
            "Quadro",
            "Fundamento_legal",
            "Orgao",
            "Vigencia"
        ]

    def _rule_for_inst(self):
        start = r"(reverter\sa\satividade[,|\s])"
        body = r"([\s\S]*?"
        end = r"(?<!lei)\s(?:[0-9|\s]*?[.|-]\s?)+?[0-9|\s]"
        end2 = r"*/\s?[0-9|\s]*-?\s?[0-9|\s]*[.|,])"
        return start + body + end + end2

    def _prop_rules(self):
        sei = r"(?<!lei)\s((?:[0-9|\s]*?[.|-]\s?)+?[0-9|\s]*/\s"
        sei2 = r"?[0-9|\s]*-?\s?[0-9|\s]*)[.|,]"
        org = r"Lotacao:|Quadro\sde\sPessoal\sd[a|e|o]([\s\S]*?)[.|,]"
        rules = {
            "processo_SEI": sei + sei2,
            "nome": r"\s([^,]*?),\smatricula",
            "matricula": r"matricula\s?n?o?\s([\s\S]*?-[\s\S]*?)[,]",
            "cargo_efetivo": r"(?:Cargo|Carreira)\sde([\s\S]*?)\,",
            "classe": r"(?:([^,]*?)\sclasse,)?(?(1)|classe\s([\s\S]*?),)",
            "padrao": r"[p|P]adr[a|ã]o\s([\s\S]*?),",
            "quadro": r"d?[e|a|o]?(Quadro[\s\S]*?)[,|;|.]",
            "fundamento_legal": r"nos\stermos\sdo\s([\s\S]*?),\sa?\s",
            "orgao": org,
            "vigencia": "",
            # "matriucla_SIAPE": r"siape\sn?o?\s([\s\S]*?)[,| | .]"
        }

        return rules
