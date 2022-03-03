"""Regras regex para ato de Aposentadoria."""

import re
import os
import joblib
from dodfminer.extract.polished.acts.base import Atos


class Retirements(Atos):
    '''
    Classe para atos de aposentadoria
    '''

    def __init__(self, file, backend):
        super().__init__(file, backend)

    def _regex_flags(self):
        return re.IGNORECASE

    def _load_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/models/aposentadoria.pkl'
        return joblib.load(f_path)

    def _load_seg_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/seg_models/aposentadoria.pkl'
        return joblib.load(f_path)

    def _act_name(self):
        return "Aposentadoria"

    def get_expected_colunms(self) -> list:
        return [
            'Ato',
            'Processo',
            'Nome_ato',
            'Cod_matricula_ato',
            'Cargo',
            'Classe',
            'Padrao',
            'Quadro',
            'Fund_legal',
            'Empresa_ato',
        ]

    def _props_names(self):
        return [
            "Ato",
            "Processo",
            "Nome_ato",
            "Cod_matricula_ato",
            # "Tipo de Aposentadoria",
            "Cargo",
            "Classe",
            "Padrao",
            "Quadro",
            "Fund_legal",
            "Empresa_ato",
            # "Vigencia",
            # "Matricula SIAPE"
        ]

    def _rule_for_inst(self):
        start = r"(APOSENTAR[^-]|CONCEDER,\sAPOSENTADORIA|CONCEDER\sAPOSENTADORIA,?\s?)"
        body = r"([\s\S]*?"
        end = r"(?<!lei)\s(?:[0-9|\s]*?[.|-]\s?)+?"
        end2 = r"[0-9|\s]*/\s?[0-9|\s]*-?\s?[0-9|\s]*[.|,])"
        return start + body + end + end2

    def _prop_rules(self):
        # siape = r"[S|s][I|i][A|a][P|p][E|e]\s[N|n]?[o|O]?\s([\s\S]*?)[,| | .]"
        sei = r"(?<!lei)\s((?:[0-9|\s]*?[.|-]\s?)+?"
        sei2 = r"[0-9|\s]*/\s?[0-9|\s]*-?\s?[0-9|\s]*)[.|,]"
        orgao = r"Lotacao:|Quadro\sde\sPessoal\sd[a|e|o]([\s\S]*?)[.|,]"
        rules = {
            "processo_SEI": sei+sei2,
            "nome": r"\s([^,]*?),\smatricula",
            "matricula": r"matricula\s?n?o?\s([\s\S]*?)[,|\s]",
            # "tipo_ret": r"",
            "cargo_efetivo": r"Cargo de([\s\S]*?)\,",
            "classe": r"[C|c]lasse\s([\s\S]*?)\,",
            "padrao": r"[p|P]adr[a|ã]o\s([\s\S]*?),",
            "quadro": r"d?[e|a|o]?(Quadro[\s\S]*?)[,|;|.]",
            "fundamento_legal": r"nos\stermos\sdo\s[a|A]rtigo([\s\S]*?),\sa?\s",
            "orgao": orgao,
            # "vigencia": r"",
            # "matricula_SIAPE": siape
        }
        return rules


class RetAposentadoria(Atos):
    '''
    Classe para atos de retificação de aposentadoria
    '''

    def __init__(self, file, backend):
        super().__init__(file, backend)

    def _regex_flags(self):
        return re.IGNORECASE

    def _act_name(self):
        return "Retificações de Aposentadoria"

    def get_expected_colunms(self) -> list:
        return [
            "Tipo de Documento",
            "Número do documento",
            "Data do documento ",
            "Número do DODF",
            "Data do DODF",
            "Página do DODF",
            "Nome do Servidor",
            "Matrícula",
            "Cargo",
            "Classe",
            "Padrao",
            "Matricula SIAPE",
            "Informação Errada",
            "Informação Corrigida"
        ]

    def _props_names(self):
        return [
            "Tipo do Ato",
            "Tipo de Documento",
            "Número do documento",
            "Data do documento ",
            "Número do DODF",
            "Data do DODF",
            "Página do DODF",
            "Nome do Servidor",
            "Matrícula",
            "Cargo",
            "Classe",
            "Padrao",
            "Matricula SIAPE",
            "Informação Errada",
            "Informação Corrigida"
        ]

    def _rule_for_inst(self):
        start = r"(RETIFICAR,\s)"
        body = r"(.*?ato\sque\sconcedeu\saposentadoria[\s\S]*?"
        end = r"\.\n)"
        return start + body + end

    def _prop_rules(self):
        tipo = r"^n[a|o]\s([\s\S]*?),?\s?(?:[0-9]*?),"
        tipo2 = r"?\sde\s(?:[0-9]*?[/|.][0-9]*?[/|.][0-9]*?|,)"

        num_doc = r"n[a|o]\s(?:[\s\S]*?),?\s?([0-9]*?),"
        num_doc2 = r"?\sde\s(?:[0-9]*?[/|.][0-9]*?[/|.][0-9]*?|,)"

        data_doc = r"n[a|o]\s(?:[\s\S]*?),?\s?(?:[0-9]*?),?\sde\s"
        data_doc2 = r"([0-9]*?[/|.][0-9]*?[/|.][0-9]*?),\s"

        data_dodf = r"dodf[\s\S]*?(?:[0-9]*?)"
        data_dodf2 = r"([0-9]*?[/|.][0-9]*?[/|.][0-9]*?)[,|\s]"

        le1 = r"\sle[,|:|;]\s?([\s\S]*?),?\sleia[\s\S]*?"
        le2 = r"[,|:|;]\s(?:[\s\S]*?)[.]\s"

        leia = r"\sle[,|:|;]\s?(?:[\s\S]*?),"
        leia2 = r"?\sleia[\s\S]*?[,|:|;]\s([\s\S]*?)[.]\s"

        rules = {
            "tipo_documento": tipo + tipo2,
            "numero_documento": num_doc + num_doc2,
            "data_documento": data_doc + data_doc2,
            "numero_dodf": r"dodf[\s\S]*?([0-9]*?),",
            "data_dodf": data_dodf + data_dodf2,
            "pagina_dodf": r"",
            "nome": r"\sa\s([^,]*?),\smatricula",
            "matricula": r"matricula\s?n?o?\s([\s\S]*?-[\s\S]*?)[,]",
            "cargo_efetivo": r"(?:Cargo|Carreira)\sde([\s\S]*?)\,",
            "classe": r"(?:([^,]*?)\sclasse,)?(?(1)|classe\s([\s\S]*?),)",
            "padrao": r"[p|P]adr[a|ã]o\s([\s\S]*?),",
            "matricula_SIAPE": r"siape\sn?o?\s([\s\S]*?)[,| | .]",
            "informacao_errada": le1+le2,
            "informacao_corrigida": leia+leia2
        }
        return rules
