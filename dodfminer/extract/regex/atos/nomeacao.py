from atos.base import Atos

class NomeacaoComissionados(Atos):
    
    def __init__(self,text):
        super().__init__(text)
    
    def _act_name(self):
        return "Nomeação"

    def _props_names(self):
        return ['Tipo', 'Nome', 'Cargo Efetivo', 'Matricula', 'Siape',
                'Simbolo', 'Cargo Comissao', 'Lotacao', 'Orgao']
        
    def _rule_for_inst(self):
        start = r"(NOMEAR)"
        body = r"([\s\S]*?)"
        end = r"\.\s"
        return start + body + end
    
    def _prop_rules(self):
        rules = {"nome": r"(^[A-ZÀ-Ž\s]+[A-ZÀ-Ž])",
                 "cargo_efetivo": r"(?:^[A-ZÀ-Ž\s]+[A-ZÀ-Ž]),\s(?![M|m]atr[i|í]cula)([\s\S]*?),\s",
                 "matricula": r"[M|m]atr[í|i]cula\s?n?o?\s([\s\S]*?)[,|\s]",
                 "siape": r"[S|s][I|i][A|a][P|p][E|e]\s[N|n]?[o|O]?\s([\s\S]*?)[,| | .]",
                 "simbolo": r"[S|s][í|i]mbolo\s?n?o?\s([\s\S]*?)[,|\s]",
                 "cargo_comissao": r"(?:[S|s][í|i]mbolo\s?n?o?\s(?:[\s\S]*?)[,|\s])\sde([\s\S]*?),",
                 "lotacao": r"(?:[S|s][í|i]mbolo\s?n?o?\s(?:[\s\S]*?)[,|\s])\sde(?:[\s\S]*?),\sd[a|e|o]\s([\s\S]*,?),",
                 "orgao": r"(?:[S|s][í|i]mbolo\s?n?o?\s(?:[\s\S]*?)[,|\s])\sde(?:[\s\S]*?),\sd[a|e|o]\s(?:[\s\S]*,?),\sd[a|e|o]\s([\s\S]*?)$"}
        return rules