"""Regras regex para ato de Aposentadoria."""

import re
from dodfminer.extract.polished.acts.base import Atos

class Retirements(Atos):
    
    def __init__(self, file, backend):
        super().__init__(file, backend)

    def _regex_flags(self):
        return re.IGNORECASE

    def _act_name(self):
        return "Aposentadoria"

    def _props_names(self):
        return ["Tipo do Ato", "SEI", "Nome", "Matrícula", "Tipo de Aposentadoria", "Cargo", "Classe",
                "Padrao", "Quadro", "Fundamento Legal", "Orgao", "Vigencia", "Matricula SIAPE"]

        
    def _rule_for_inst(self):
        start = "(APOSENTAR|CONCEDER\sAPOSENTADORIA,?\s?)"
        body = "([\s\S]*?"
        # end = "[P|p]rocesso:?\s[s|S]?[e|E]?[i|I]?\s?[n|N]?[o|O]?\s?[\s\S]*?.\s)"
        end = "(?<!lei)\s(?:[0-9|\s]*?[.|-]\s?)+?[0-9|\s]*/\s?[0-9|\s]*-?\s?[0-9|\s]*[.|,])"
        return start + body + end
    
    def _prop_rules(self):
        rules = {"sei": "(?<!lei)\s((?:[0-9|\s]*?[.|-]\s?)+?[0-9|\s]*/\s?[0-9|\s]*-?\s?[0-9|\s]*)[.|,]",
                 "nome": "\s([^,]*?),\smatricula",
                 "matricula":"matricula\s?n?o?\s([\s\S]*?)[,|\s]",
                 "tipo_ret": "",
                 "cargo": "Cargo de([\s\S]*?)\,",
                 "classe": "[C|c]lasse\s([\s\S]*?)\,",
                 "padrao": "[p|P]adr[a|ã]o\s([\s\S]*?),",
                 "quadro": "d?[e|a|o]?(Quadro[\s\S]*?)[,|;|.]",
                 "fundamento": "nos\stermos\sdo\s[a|A]rtigo([\s\S]*?),\sa?\s",
                 "orgao": "Lotacao:|Quadro\sde\sPessoal\sd[a|e|o]([\s\S]*?)[.|,]",
                 "vigencia": "",
                 "siape": "[S|s][I|i][A|a][P|p][E|e]\s[N|n]?[o|O]?\s([\s\S]*?)[,| | .]"} 
        return rules