"""Regras regex para atos de Reversões."""

import re
from dodfminer.extract.polished.acts.base import Atos


class Revertions(Atos):

    def __init__(self, text):
        super().__init__(text)

    def _regex_flags(self):
        return re.IGNORECASE

    def _act_name(self):
        return "Reversão"

    def _props_names(self):
        return ["Tipo do Ato", "SEI", "Nome", "Matricula", "Cargo", "Classe",
                "Padrao", "Quadro", "Fundamento Legal", "Orgao",
                "Vigencia", "Matricula SIAPE"]

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
        rules = {"sei": sei + sei2,
                 "nome": r"\s([^,]*?),\smatricula",
                 "matricula": r"matricula\s?n?o?\s([\s\S]*?-[\s\S]*?)[,]",
                 "cargo": r"(?:Cargo|Carreira)\sde([\s\S]*?)\,",
                 "classe": r"(?:([^,]*?)\sclasse,)?(?(1)|classe\s([\s\S]*?),)",
                 "padrao": r"[p|P]adr[a|ã]o\s([\s\S]*?),",
                 "quadro": r"d?[e|a|o]?(Quadro[\s\S]*?)[,|;|.]",
                 "fundamento": r"nos\stermos\sdo\s([\s\S]*?),\sa?\s",
                 "orgao": org,
                 "vigencia": "",
                 "siape": r"siape\sn?o?\s([\s\S]*?)[,| | .]"}

        return rules
