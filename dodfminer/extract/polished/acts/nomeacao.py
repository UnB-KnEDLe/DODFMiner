"""Regras regex para ato de Nomeacao de Comissionados."""

from dodfminer.extract.polished.acts.base import Atos


class NomeacaoComissionados(Atos):
    
    def __init__(self, file, backend):
        super().__init__(file, backend)
    
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
        eft = r"(?:^[A-ZÀ-Ž\s]+[A-ZÀ-Ž]),\s(?![M|m]atr[i|í]cula)([\s\S]*?),\s"
        siape = r"[S|s][I|i][A|a][P|p][E|e]\s[N|n]?[o|O]?\s([\s\S]*?)[,| | .]"
        coms = r"(?:[S|s][í|i]mbolo\s?n?o?\s(?:[\s\S]*?)[,|\s])\sde([\s\S]*?),"
        lot = r"(?:[S|s][í|i]mbolo\s?n?o?\s(?:[\s\S]*?)[,|\s])"
        lot2 = r"\sde(?:[\s\S]*?),\sd[a|e|o]\s([\s\S]*,?),"
        org = r"(?:[S|s][í|i]mbolo\s?n?o?\s(?:[\s\S]*?)[,|\s])\sde(?:[\s\S]*?)"
        org2 = r",\sd[a|e|o]\s(?:[\s\S]*,?),\sd[a|e|o]\s([\s\S]*?)$"

        rules = {"nome": r"(^[A-ZÀ-Ž\s]+[A-ZÀ-Ž])",
                 "efetivo": eft,
                 "matricula": r"[M|m]atr[í|i]cula\s?n?o?\s([\s\S]*?)[,|\s]",
                 "siape": siape,
                 "simbolo": r"[S|s][í|i]mbolo\s?n?o?\s([\s\S]*?)[,|\s]",
                 "comissao": coms,
                 "lotacao": lot + lot2,
                 "orgao": org + org2}
        return rules
