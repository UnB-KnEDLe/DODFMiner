from dodfminer.extract.regex.atos.base import Atos

class Exoneracao(Atos):
    
    def __init__(self,text):
        super().__init__(text)
    
    def _act_name(self):
        return "Exoneração"

    def _props_names(self):
        return ['tipo', 'nome','matricula','simbolo','cargo_comissao','lotacao','orgao','vigencia','pedido',
                'cargo_efetivo','siape','motivo']
        
    def _rule_for_inst(self):
        start = r"(EXONERAR)"
        body = r"([\s\S]*?)"
        end = "\."
        return start + body + end
    
    def _prop_rules(self):
        rules = {"nome": r"([A-ZÀ-Ž\s]+[A-ZÀ-Ž])",
                "matricula": r"matr[í|i]cula\s?n?o?\s([\s\S]*?)[,|\s]",
                "simbolo": r"[S|s][í|i]mbolo\s?n?o?\s([\s\S]*?)[,|\s]",
                "cargo_comissao": "",
                "lotacao": "",
                "orgao": "",
                "vigencia": "",
                "pedido": r"(a pedido)",
                "cargo_efetivo": "",
                "siape": r"[S|s][I|i][A|a][P|p][E|e]\s[N|n]*[o|O]*\s?([\s\S]*?)[,| | .]",
                "motivo": ""}
             
        return rules