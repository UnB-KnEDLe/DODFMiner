import re
from dodfminer.extract.regex.atos.base import Atos

class AbonoPermanencia(Atos):    

    def __init__(self, file):
        super().__init__(file)

    def _regex_flags(self):
        return re.IGNORECASE

    def _act_name(self):
        return "Abono de Permanência"

    def _props_names(self):
        return ["Tipo do Ato", "Nome do Servidor", "Matrícula", "Cargo Efetivo", "Classe", 
                "Padrão", "Quadro pessoal permanente ou Suplementar",
                "Fundamento Legal do abono de permanência", "Órgão",
                "Processo GDF/SEI", "Vigencia", "Matricula SIAPE"]
        
        
    def _rule_for_inst(self):
        start = "(Abono\sDE\sPERMANENCIA\s[(ao|equiva)][\s\S]*?)\s"
        body = "([\s\S]*?"
        end = "\.\n)"
        return start + body + end
    
    def _prop_rules(self):
        rules = {"nome": "\s([^,]*?),\smatricula",
                 "matricula":"matricula\s?n?o?\s([\s\S]*?)[,|\s]",
                 "cargo": "Cargo\s[d|D]?[e|E]?\s([\s\S]*?),",
                 "classe": "[C|c]lasse\s([\s\S]*?),",
                 "padrao": "[p|P]adr[a|ã]o\s([\s\S]*?),",
                 "quadro": "d?[e|a|o]?(Quadro[\s\S]*?)[,|;|.]",
                 "fundamento": "nos\stermos\sdo\s([\s\S]*?),\sa?\s",
                 "orgao": "Lotacao: ([\s\S]*?)[.]",
                 "sei": "Processo SEI: ([\s\S]*?)\.\n",
                 "vigencia": "a contar de ([\s\S]*?)\,",
                 "siape": "[S|s][I|i][A|a][P|p][E|e]\s[N|n]?[o|O]?\s([\s\S]*?)[,| | .]"}
        return rules