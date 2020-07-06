from atos.base import Atos

class Exoneracao(Atos):

    def __init__(self,text):
        super().__init__(text)

    def _act_name(self):
        return "Exoneração"

    def _props_names(self):
        return ['tipo','nome','matricula','simbolo','cargo_comissao','lotacao','orgao','vigencia','pedido',
                'cargo_efetivo','siape','motivo']

    def _rule_for_inst(self):
        start = r"(EXONERAR)"
        body = r"([\s\S]*?)"
        end = "\."
        return start + body + end

    def _prop_rules(self):
        rules = {"nome": r"([A-ZÀ-Ž\s]+[A-ZÀ-Ž])",
                "matricula":"matricula\s?n?o?\s([\s\S]*?-[\s\S]*?)[,]",
                "simbolo": r"[S|s][í|i]mbolo\s?n?o?\s([\s\S]*?)[,|\s]",
                "cargo_comissao": "(?:Cargo|Carreira)\sde([\s\S]*?)\,",
                "lotacao": r"(?:[S|s][í|i]mbolo\s?n?o?\s(?:[\s\S]*?)[,|\s])\sde(?:[\s\S]*?),\sd[a|e|o]\s([\s\S]*,?),",
                "orgao": r"(?:[S|s][í|i]mbolo\s?n?o?\s(?:[\s\S]*?)[,|\s])\sde(?:[\s\S]*?),\sd[a|e|o]\s(?:[\s\S]*,?),\sd[a|e|o]\s([\s\S]*?)$",
                "vigencia": "",
                "pedido": r"(a pedido)",
                "cargo_efetivo": "",
                "siape": r"[S|s][I|i][A|a][P|p][E|e]\s[N|n]*[o|O]*\s?([\s\S]*?)[,| | .]",
                "motivo": ""}

        return rules
