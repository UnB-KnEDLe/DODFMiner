"""Regras regex para ato de Abono de Permanencia."""

import re
import os
import joblib
from dodfminer.extract.polished.acts.base import Atos


class AbonoPermanencia(Atos):

    def __init__(self, file, backend):
        super().__init__(file, backend)

    def _regex_flags(self):
        return re.IGNORECASE

    def _act_name(self):
        return "Abono de Permanência"

    def _load_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/models/abono_ner.pkl'
        return joblib.load(f_path)

    def _props_names(self):
        return ["Tipo do Ato", "Nome do Servidor", "Matrícula",
                "Cargo Efetivo", "Classe", "Padrão",
                "Quadro pessoal permanente ou Suplementar",
                "Fundamento Legal do abono de permanência", "Órgão",
                "Processo GDF/SEI", "Vigencia", "Matricula SIAPE"]

    def _rule_for_inst(self):
        start = r"(Abono\sDE\sPERMANENCIA\s[(ao|equiva)][\s\S]*?)\s"
        body = r"([\s\S]*?"
        end = r"\.\n)"
        return start + body + end

    def _prop_rules(self):
        siape = r"[S|s][I|i][A|a][P|p][E|e]\s[N|n]?[o|O]?\s([\s\S]*?)[,| | .]"
        rules = {"nome": r"\s([^,]*?),\smatricula",
                 "matricula": r"matricula\s?n?o?\s([\s\S]*?)[,|\s]",
                 "cargo": r"Cargo\s[d|D]?[e|E]?\s([\s\S]*?),",
                 "classe": r"[C|c]lasse\s([\s\S]*?),",
                 "padrao": r"[p|P]adr[a|ã]o\s([\s\S]*?),",
                 "quadro": r"d?[e|a|o]?(Quadro[\s\S]*?)[,|;|.]",
                 "fundamento": r"nos\stermos\sdo\s([\s\S]*?),\sa?\s",
                 "orgao": r"Lotacao: ([\s\S]*?)[.]",
                 "sei": r"Processo SEI: ([\s\S]*?)\.\n",
                 "vigencia": r"a contar de ([\s\S]*?)\,",
                 "siape": siape}
        return rules
