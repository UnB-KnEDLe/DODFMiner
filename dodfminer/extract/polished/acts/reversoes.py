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
               "Padrao", "Quadro", "Fundamento Legal", "Orgao", "Vigencia", "Matricula SIAPE"]
        
    def _rule_for_inst(self):
        start = "(reverter\sa\satividade[,|\s])"
        body = "([\s\S]*?"
        end = "(?<!lei)\s(?:[0-9|\s]*?[.|-]\s?)+?[0-9|\s]*/\s?[0-9|\s]*-?\s?[0-9|\s]*[.|,])"
        return start + body + end
    
    def _prop_rules(self):
        rules = {"sei": "(?<!lei)\s((?:[0-9|\s]*?[.|-]\s?)+?[0-9|\s]*/\s?[0-9|\s]*-?\s?[0-9|\s]*)[.|,]",
                 "nome": "\s([^,]*?),\smatricula",
                 "matricula":"matricula\s?n?o?\s([\s\S]*?-[\s\S]*?)[,]",
                 "cargo": "(?:Cargo|Carreira)\sde([\s\S]*?)\,",
                 "classe": "(?:([^,]*?)\sclasse,)?(?(1)|classe\s([\s\S]*?),)",
                 "padrao": "[p|P]adr[a|ã]o\s([\s\S]*?),",
                 "quadro": "d?[e|a|o]?(Quadro[\s\S]*?)[,|;|.]",
                 "fundamento": "nos\stermos\sdo\s([\s\S]*?),\sa?\s",
                 "orgao": "Lotacao:|Quadro\sde\sPessoal\sd[a|e|o]([\s\S]*?)[.|,]",
                 "vigencia": "",
                 "siape": "siape\sn?o?\s([\s\S]*?)[,| | .]"}
             
        return rules