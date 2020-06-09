import re
from dodfminer.extract.regex.atos.base import Atos

class Revertions(Atos):

    def __init__(self, text):
        super().__init__(text)

    def _regex_flags(self):
        return re.IGNORECASE

    def _act_name(self):
        return "Reversão"

    def _props_names(self):
        return ["Tipo do Ato", "SEI", "Nome", "Matrícula", "Cargo", "Classe",
               "Padrao", "Quadro", "Fundamento Legal", "Orgao", "Vigencia", "Matricula SIAPE"]
        
    def _rule_for_inst(self):
        start = "(reverter\sa\satividade[,|\s])"
        body = "([\s\S]*?"
        end = "processo\s[\s\S]*?[.]\s)"
        # end = "[P|p]rocesso:?\s[s|S]?[e|E]?[i|I]?\s?[n|N]?[o|O]?\s?([\s\S]*?)[.]\s"
        # end2 = "Processo\sde\sReversao:?\sn?\s?([\s\S]*?)[.]\s"
        # end3 = "Processo\sde\sReversao\sSigiloso:?\s([\s\S]*?)[.]\s"
        # end4 = "Processo\sde\sReversao\sPGDF\sSEI:?\s([\s\S]*?)[.]\s"
        return start + body + end
    
    def _prop_rules(self):
        rules = {"sei": "processo\s([\s\S]*?).\s",
                 "nome": "\s([^,]*?),\smatricula",
                 "matricula":"matricula\s?n?o?\s([\s\S]*?)[,| ]",
                 "cargo": "[C|c]argo\s[d|D]?[e|E]?\s([\s\S]*?),",
                 "classe": "[C|c]lasse\s([\s\S]*?),",
                 "padrao": "[p|P]adr[a|ã]o\s([\s\S]*?),",
                 "quadro": "d?[e|a|o]?(Quadro[\s\S]*?)[,|;|.]",
                 "fundamento": "nos\stermos\sdo\s([\s\S]*?),\sa?\s",
                 "orgao": "Lotacao: ([\s\S]*?)[.]",
                 "vigencia": "",
                 "siape": ""}
             
        return rules