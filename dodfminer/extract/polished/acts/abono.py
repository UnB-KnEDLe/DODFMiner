"""Regras regex para ato de Abono de Permanencia."""

import re
import os
import joblib
from dodfminer.extract.polished.acts.base import Atos


class AbonoPermanencia(Atos):
    '''
    Classe para atos de abono
    '''

    def __init__(self, file, backend):
        super().__init__(file, backend)

    def _regex_flags(self):
        return re.IGNORECASE | re.MULTILINE

    def _act_name(self):
        return "Abono de Permanência"

    def _load_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/models/abono.pkl'
        return joblib.load(f_path)

    def _load_seg_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/seg_models/abono.pkl'
        return joblib.load(f_path)

    def get_expected_colunms(self) -> list:
        return [
            'Nome',
            'Matricula',
            'Cargo_efetivo',
            'Classe',
            'Padrao',
            'Quadro',
            'Fundamento_legal',
            'Orgao',
            'Processo_sei',
            'Vigencia',
            'Matricula_siape',
            # Problematicos que estão no modelos ner
            'Cargo',
            'Lotacao'
        ]

    def _props_names(self):
        return [
            'Tipo do Ato',
            'Nome',
            'Matricula',
            'Cargo_efetivo',
            'Classe',
            'Padrao',
            'Quadro',
            'Fundamento_legal',
            'Orgao',
            'Processo_sei',
            'Vigencia',
            'Matricula_siape',
            # Problematicos que estão no modelos ner
            'Cargo',
            'Lotacao'
        ]

    def _rule_for_inst(self):
        start = r"(Abono\sDE\sPERMANENCIA\s[(ao|equiva)][\s\S]*?)\s"
        body = r"([\s\S]*?"
        end = r"\d+\s*[\.|\-]\s*\d+\s*\/\s*\d+\s*\-\s*\d+)"
        return start + body + end

    def _prop_rules(self):
        siape = r"[S|s][I|i][A|a][P|p][E|e]\s[N|n]?[o|O]?\s([\s\S]*?)[,| | .]"
        rules = {
            "nome": r"\s([^,]*?),\smatricula",
            "matricula": r"matricula\s?n?o?\s([\s\S]*?)[,|\s]",
            "cargo_efetivo": r"Cargo\s[d|D]?[e|E]?\s([\s\S]*?),",
            "classe": r"[C|c]lasse\s([\s\S]*?),",
            "padrao": r"[p|P]adr[a|ã]o\s([\s\S]*?),",
            "quadro": r"d?[e|a|o]?(Quadro[\s\S]*?)[,|;|.]",
            "fundamento_legal_abono_permanencia": r"nos\stermos\sdo\s([\s\S]*?),\sa?\s",
            "orgao": r"Lotacao: ([\s\S]*?)[.]",
            "processo_SEI": r"Processo SEI: ([\s\S]*?)\.\n",
            "vigencia": r"a contar de ([\s\S]*?)\,",
            "matricula_SIAPE": siape,
            # Problematicos que estão no modelos ner
            'cargo': r'',
            'lotacao': r''
        }
        return rules
