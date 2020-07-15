"""Regras regex para ato de Aposentadoria."""

import re
from dodfminer.extract.polished.acts.base import Atos


class Retirements(Atos):
    
    def __init__(self, file, backend):
        super().__init__(file, backend)

    def _regex_flags(self):
        return re.IGNORECASE

    # def _load_model(self):
    #     f_path = os.path.dirname(__file__)
    #     f_path += '/models/aposentadoria_ner.pkl'
    #     return joblib.load(f_path)

    def _act_name(self):
        return "Aposentadoria"

    def _props_names(self):
        return ["Tipo do Ato", "SEI", "Nome", "Matrícula",
                "Tipo de Aposentadoria", "Cargo", "Classe", "Padrao", "Quadro",
                "Fundamento Legal", "Orgao", "Vigencia", "Matricula SIAPE"]

    def _rule_for_inst(self):
        start = r"(APOSENTAR|CONCEDER\sAPOSENTADORIA,?\s?)"
        body = r"([\s\S]*?"
        end = r"(?<!lei)\s(?:[0-9|\s]*?[.|-]\s?)+?"
        end2 = r"[0-9|\s]*/\s?[0-9|\s]*-?\s?[0-9|\s]*[.|,])"
        return start + body + end + end2

    def _prop_rules(self):
        siape = r"[S|s][I|i][A|a][P|p][E|e]\s[N|n]?[o|O]?\s([\s\S]*?)[,| | .]"
        sei = r"(?<!lei)\s((?:[0-9|\s]*?[.|-]\s?)+?"
        sei2 = r"[0-9|\s]*/\s?[0-9|\s]*-?\s?[0-9|\s]*)[.|,]"
        orgao = r"Lotacao:|Quadro\sde\sPessoal\sd[a|e|o]([\s\S]*?)[.|,]"
        rules = {"sei": sei+sei2,
                 "nome": r"\s([^,]*?),\smatricula",
                 "matricula": r"matricula\s?n?o?\s([\s\S]*?)[,|\s]",
                 "tipo_ret": r"",
                 "cargo": r"Cargo de([\s\S]*?)\,",
                 "classe": r"[C|c]lasse\s([\s\S]*?)\,",
                 "padrao": r"[p|P]adr[a|ã]o\s([\s\S]*?),",
                 "quadro": r"d?[e|a|o]?(Quadro[\s\S]*?)[,|;|.]",
                 "fundamento": r"nos\stermos\sdo\s[a|A]rtigo([\s\S]*?),\sa?\s",
                 "orgao": orgao,
                 "vigencia": r"",
                 "siape": siape}
        return rules

class RetAposentadoria(Atos):

    def __init__(self, file):
        super().__init__(file)

    def _regex_flags(self):
        return re.IGNORECASE

    def _act_name(self):
        return "Retificações de Aposentadoria"

    def _props_names(self):
        return ["Tipo do Ato", "Tipo de Documento", "Número do documento",
                "Data do documento ", "Número do DODF", "Data do DODF",
                "Página do DODF", "Nome do Servidor", "Matrícula", "Cargo",
                "Classe", "Padrao", "Matricula SIAPE",
                "Informação Errada", "Informação Corrigida"]

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

        le = r"\sle[,|:|;]\s?([\s\S]*?),?\sleia[\s\S]*?"
        le2 = r"[,|:|;]\s(?:[\s\S]*?)[.]\s"

        leia = r"\sle[,|:|;]\s?(?:[\s\S]*?),"
        leia2 = r"?\sleia[\s\S]*?[,|:|;]\s([\s\S]*?)[.]\s"

        rules = {"tipo_doc": tipo + tipo2,
                 "num_doc": num_doc + num_doc2,
                 "data_doc": data_doc + data_doc2,
                 "num_dodf": r"dodf[\s\S]*?([0-9]*?),",
                 "data_dodf": data_dodf + data_dodf2,
                 "pag_dodf": r"",
                 "nome": r"\sa\s([^,]*?),\smatricula",
                 "matricula": r"matricula\s?n?o?\s([\s\S]*?-[\s\S]*?)[,]",
                 "cargo": r"(?:Cargo|Carreira)\sde([\s\S]*?)\,",
                 "classe": r"(?:([^,]*?)\sclasse,)?(?(1)|classe\s([\s\S]*?),)",
                 "padrao": r"[p|P]adr[a|ã]o\s([\s\S]*?),",
                 "siape": r"siape\sn?o?\s([\s\S]*?)[,| | .]",
                 "le": le+le2,
                 "leiase": leia+leia2}
        return rules
