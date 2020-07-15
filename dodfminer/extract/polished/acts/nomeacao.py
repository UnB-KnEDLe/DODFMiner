"""Regras regex para ato de Nomeacao de Comissionados."""

from dodfminer.extract.polished.acts.base import Atos


class NomeacaoComissionados(Atos):

    def __init__(self, text, backend):
        super().__init__(text, backend)

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

class NomeacaoEfetivos(Atos):

    def __init__(self,text):
        super().__init__(text)

    def _act_name(self):
        return "Nomeação de Efetivos"

    def _props_names(self):
        return ['tipo','edital_normativo','data_do_edital_normativo','DODF_edital_normativo','data_DODF_edital_normativo','edital_resultado_final','data_edital_resultado_final','cargo','especialiade','carreira','orgao','nome_candidato','classificacao','pne','sei','reposicionamento']

    def _rule_for_inst(self):
        start = r"(NOMEAR\s)((?:[ao]s\scandidat[ao]s\sabaixo(?:[a-zA-Z_0-9,\s\/-\:\-\(\);]*).|(?:[ao]\scandidat[oa]\sabaixo(?:[a-zA-Z_0-9,\s\/-\:\-\(\)]*)))(?:\s[a-zA-Z_\s]*(?:deficiencia|especiais):(?:\s[\sA-Zo]+,\s?\d{1,4}o?;?)+)?(?:\s)?(?:[\r\n\t\f\sa-zA-Z_\s]*classificacao:(?:\s[\sA-Zo]+,\s?\d{1,4}o?[,;]?)+)?)"
        body = ""
        end = ""
        return start + body + end

    def _prop_rules(self):
        rules = rules = {"edital_normativo": r"Edital\s(?:[Nn]ormativo|de\s[Aa]bertura)\sno\s([\/\s\-a-zA-Z0-9_]+)",
                         "data_do_edital_normativo": r"",
                         "DODF_edital_normativo": r"publicado\sno\sDODF\sno\s(\d{1,3})",
                         "data_DODF_edital_normativo": r"publicado\sno\sDODF\sno\s\d{1,3},\s?de([\s0-9a-or-vzç]*\d{4})",
                         "edital_resultado_final": r"Resultado\sFinal\sno\s([\/\s\-a-zA-Z0-9_]+)",
                         "data_edital_resultado_final": r"",
                         "cargo": r"DODF\sno\s\d{1,3}(?:,[\s0-9a-or-vzç]*\d{4}),[\sa-z]*([A-Z\s]+)",
                         "especialiade": r"[\s,a-z\(\:\)]+([\sA-Z\-]*):",
                         "carreira": r"[cC]arreira\s(?:d[ae]\s)?([a-zA-Z\s]+)",
                         "orgao": r"[cC]arreira\s(?:d[ae]\s)?(?:[a-zA-Z\s]+),\s?d?[ao]?\s?([\sa-zA-Z0-9_]*)",
                         "nome_candidato": r"(?:[\sA-Z\-]*):(?:[\sa-zC]*:)?\s([\sA-Z0-9\,o\;]+)",
                         "classificacao": r"",
                         "pne": r"(?:deficiencia|especiais):\s([\sA-Z0-9\,o\;]+)",
                         "sei": r"(?<!lei)\s((?:[0-9|\s]*?[.|-]\s?)+?[0-9|\s]*/\s?[0-9|\s]*-?\s?[0-9|\s]*)[.|,]",
                         "reposicionamento": r"lista\sde\sclassificacao:\s([\sA-Z0-9\,o\;]+)"}
        return rules
