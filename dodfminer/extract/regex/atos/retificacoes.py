from dodfminer.extract.regex.atos.base import Atos

class RetAposentadoria(Atos):

    def __init__(self, file):
        super().__init__(file)

    def _act_name(self):
        return "Retificações de Aposentadoria"

    def _props_names(self):
        return ["Tipo de Documento", "Número do documento", "Data do documento ",
                "Número do DODF", "Data do DODF", "Página do DODF", "Nome do Servidor",
                "Matrícula", "Cargo", "Classe", "Padrao", "Matricula SIAPE",
                "Informação Errada", "Informação Corrigida"]
        
        
    def _rule_for_inst(self):
        start = "(RETIFICAR,.*?ato\sque\sconcedeu\saposentadoria[\s\S]*?)"
        body = ""
        end = "(\.\n)"
        return start + body + end
    
    def _prop_rules(self):
        rules = {"Tipo doc": "",
                 "Num doc": "",
                 "Data doc": "",
                 "Num dodf": "",
                 "Data dodf": "",
                 "Pag dodf": "",
                 "nome": "\s([^,]*?),\smatricula",
                 "matricula":"matricula\s?n?o?\s([\s\S]*?)[,|\s]",
                 "cargo": "Cargo\s[d|D]?[e|E]?\s([\s\S]*?),",
                 "classe": "[C|c]lasse\s([\s\S]*?),",
                 "padrao": "[p|P]adr[a|ã]o\s([\s\S]*?),",
                 "siape": "[S|s][I|i][A|a][P|p][E|e]\s[N|n]?[o|O]?\s([\s\S]*?)[,| | .]",
                 "Info errada": "",
                 "Info corrigida": ""}
        return rules