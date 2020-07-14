"""Regras regex para ato de Exoneração."""

from dodfminer.extract.polished.acts.base import Atos


class Exoneracao(Atos):

    def __init__(self, text):
        super().__init__(text)

    def _act_name(self):
        return "Exoneração"

    def _props_names(self):
        return ['tipo', 'nome', 'matricula', 'simbolo', 'cargo_comissao',
                'lotacao', 'orgao', 'vigencia', 'pedido', 'cargo_efetivo',
                'siape', 'motivo']

    def _rule_for_inst(self):
        start = r"(EXONERAR)"
        body = r"([\s\S]*?)"
        end = r"\."
        return start + body + end

    def _prop_rules(self):
        siape = r"[S|s][I|i][A|a][P|p][E|e]\s[N|n]*[o|O]*\s?([\s\S]*?)[,| | .]"
        lot1 = r"(?:[S|s][í|i]mbolo\s?n?o?\s(?:[\s\S]*?)[,|\s])"
        lot2 = r"\sde(?:[\s\S]*?),\sd[a|e|o]\s([\s\S]*,?),"
        org = r"(?:[S|s][í|i]mbolo\s?n?o?\s(?:[\s\S]*?)[,|\s])\sde(?:[\s\S]*?)"
        org2 = r",\sd[a|e|o]\s(?:[\s\S]*,?),\sd[a|e|o]\s([\s\S]*?)$"
        rules = {"nome": r"([A-ZÀ-Ž\s]+[A-ZÀ-Ž])",
                 "matricula": r"matricula\s?n?o?\s([\s\S]*?-[\s\S]*?)[,]",
                 "simbolo": r"[S|s][í|i]mbolo\s?n?o?\s([\s\S]*?)[,|\s]",
                 "cargo_comissao": r"(?:Cargo|Carreira)\sde([\s\S]*?)\,",
                 "lotacao": lot1 + lot2,
                 "orgao": org + org2,
                 "vigencia": r"",
                 "pedido": r"(a pedido)",
                 "cargo_efetivo": r"",
                 "siape": siape,
                 "motivo": r""}

        return rules
