"""Regras regex para ato de Retificação de Aposentadorias."""

import re
from dodfminer.extract.regex.atos.base import Atos

class RetAposentadoria(Atos):

    def __init__(self, file):
        super().__init__(file)

    def _regex_flags(self):
        return re.IGNORECASE

    def _act_name(self):
        return "Retificações de Aposentadoria"

    def _props_names(self):
        return ["Tipo do Ato", "Tipo de Documento", "Número do documento", "Data do documento ",
                "Número do DODF", "Data do DODF", "Página do DODF", "Nome do Servidor",
                "Matrícula", "Cargo", "Classe", "Padrao", "Matricula SIAPE",
                "Informação Errada", "Informação Corrigida"]
        
        
    def _rule_for_inst(self):
        start = "(RETIFICAR,\s)"
        body = "(.*?ato\sque\sconcedeu\saposentadoria[\s\S]*?"
        end = "\.\n)"
        return start + body + end
    
    def _prop_rules(self):
        rules = {"tipo_doc": "^n[a|o]\s([\s\S]*?),?\s?(?:[0-9]*?),?\sde\s(?:[0-9]*?[/|.][0-9]*?[/|.][0-9]*?|,)",
                 "num_doc": "n[a|o]\s(?:[\s\S]*?),?\s?([0-9]*?),?\sde\s(?:[0-9]*?[/|.][0-9]*?[/|.][0-9]*?|,)",
                 "data_doc": "n[a|o]\s(?:[\s\S]*?),?\s?(?:[0-9]*?),?\sde\s([0-9]*?[/|.][0-9]*?[/|.][0-9]*?),\s",
                 "num_dodf": "dodf[\s\S]*?([0-9]*?),",
                 "data_dodf": "dodf[\s\S]*?(?:[0-9]*?)([0-9]*?[/|.][0-9]*?[/|.][0-9]*?)[,|\s]",
                 "pag_dodf": "",
                 "nome": "\sa\s([^,]*?),\smatricula",
                 "matricula":"matricula\s?n?o?\s([\s\S]*?-[\s\S]*?)[,]",
                 "cargo": "(?:Cargo|Carreira)\sde([\s\S]*?)\,",
                 "classe": "(?:([^,]*?)\sclasse,)?(?(1)|classe\s([\s\S]*?),)",
                 "padrao": "[p|P]adr[a|ã]o\s([\s\S]*?),",
                 "siape": "siape\sn?o?\s([\s\S]*?)[,| | .]",
                 "le": "\sle[,|:|;]\s?([\s\S]*?),?\sleia[\s\S]*?[,|:|;]\s(?:[\s\S]*?)[.]\s",
                 "leiase": "\sle[,|:|;]\s?(?:[\s\S]*?),?\sleia[\s\S]*?[,|:|;]\s([\s\S]*?)[.]\s"}
        return rules