"""Regras regex para ato de Aposentadoria."""

import re
from dodfminer.extract.polished.acts.base import Atos


class Retirements(Atos):

    def __init__(self, file):
        super().__init__(file)

    def _regex_flags(self):
        return re.IGNORECASE

    def _act_name(self):
        return "Aposentadoria"

    def _props_names(self):
        return ["Tipo do Ato", "SEI", "Nome", "Matrícula",
                "Tipo de Aposentadoria", "Cargo", "Classe", "Padrao", "Quadro",
                "Fundamento Legal", "Orgao", "Vigencia", "Matricula SIAPE"]

    def _rule_for_inst(self):
        start = r"(APOSENTAR|CONCEDER\sAPOSENTADORIA,?\s?)"
        body = r"([\s\S]*?"
        end = r"(?<!lei)\s(?:[0-9|\s]*?[.|-]\s?)+?"
        end2 = r"[0-9|\s]*/\s?[0-9|\s]*-?\s?[0-9|\s]*[.|,])"
        return start + body + end + end2

    def _prop_rules(self):
        siape = r"[S|s][I|i][A|a][P|p][E|e]\s[N|n]?[o|O]?\s([\s\S]*?)[,| | .]"
        sei = r"(?<!lei)\s((?:[0-9|\s]*?[.|-]\s?)+?"
        sei2 = r"[0-9|\s]*/\s?[0-9|\s]*-?\s?[0-9|\s]*)[.|,]"
        orgao = r"Lotacao:|Quadro\sde\sPessoal\sd[a|e|o]([\s\S]*?)[.|,]"
        rules = {"sei": sei+sei2,
                 "nome": r"\s([^,]*?),\smatricula",
                 "matricula": r"matricula\s?n?o?\s([\s\S]*?)[,|\s]",
                 "tipo_ret": r"",
                 "cargo": r"Cargo de([\s\S]*?)\,",
                 "classe": r"[C|c]lasse\s([\s\S]*?)\,",
                 "padrao": r"[p|P]adr[a|ã]o\s([\s\S]*?),",
                 "quadro": r"d?[e|a|o]?(Quadro[\s\S]*?)[,|;|.]",
                 "fundamento": r"nos\stermos\sdo\s[a|A]rtigo([\s\S]*?),\sa?\s",
                 "orgao": orgao,
                 "vigencia": r"",
                 "siape": siape}
        return rules
