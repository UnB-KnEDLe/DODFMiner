from dodfminer.extract.regex.atos.base import Atos

class NomeacaoComissionados(Atos):
    
    def __init__(self,text):
        super().__init__(text)
    
    def _act_name(self):
        return "Nomeação"

    def _props_names(self):
        return ['tipo','nome','cargo_efetivo','matricula','siape','simbolo','cargo_comissao','lotacao','orgao']
        
    def _rule_for_inst(self):
        start = r"(NOMEAR)"
        body = r"([\s\S]*?)"
        end = "\."
        return start + body + end
    
    def _prop_rules(self):
        rules = rules = {"nome": r"(^[A-ZÀ-Ž\s]+[A-ZÀ-Ž])",
                         "cargo_efetivo": r"",
                         "matricula": r"matr[í|i]cula\s?n?o?\s([\s\S]*?)[,|\s]",
                         "siape": r"[S|s][I|i][A|a][P|p][E|e]\s[N|n]?[o|O]?\s([\s\S]*?)[,| | .]",
                         "simbolo": r"[S|s][í|i]mbolo\s?n?o?\s([\s\S]*?)[,|\s]",
                         "cargo_comissao": "",
                         "lotacao": "",
                         "orgao": ""}
        return rules