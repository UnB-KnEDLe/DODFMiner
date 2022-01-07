"""Regras regex para ato de Exoneração."""

import re
import os
import joblib
from dodfminer.extract.polished.acts.base import Atos


class Exoneracao(Atos):
    '''
        Classe para atos de exoneração não-efetivos
    '''

    def __init__(self, file, backend):
        super().__init__(file, backend)

    def _act_name(self):
        return "Exoneração"

    def _load_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/models/comissionados_exo.pkl'
        return joblib.load(f_path)

    def _load_seg_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/seg_models/comissionados_exo.pkl'
        return joblib.load(f_path)

    def _props_names(self):
        return ['Tipo do Ato', 'nome', 'matricula', 'simbolo', 'cargo_comissao',
                'lotacao', 'orgao', 'vigencia', 'pedido', 'cargo_efetivo',
                'siape', 'motivo']

    def _rule_for_inst(self):
        start = r"(EXONERAR)"
        body = r'((?=.*Comissao|.*\n.*Comissao|.*Especial|.*\n.*Especial )[\s\S]*?'
        end = r"(?:\.\n|NOMEAR|\d+\-\d+\/\d+\-\d+\.))"
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
                 "cargo_comissionado": r"(?:Cargo|Carreira)\sde([\s\S]*?)\,",
                 "hierarqui_lotacao": lot1 + lot2,
                 "orgao": org + org2,
                 "vigencia": r"",
                 "a_pedido_ou_nao": r"(a pedido)",
                 "cargo_efetivo": r"",
                 "matricula_SIAPE": siape,
                 "motivo": r""}
        return rules

class ExoneracaoEfetivos(Atos):
    '''
        Classe para atos de exoneração efetivos
    '''

    def __init__(self, file, backend):
        super().__init__(file, backend)

    def _act_name(self):
        return "Exoneração Efetivos"

    def _load_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/models/efetivos_exo.pkl'
        return joblib.load(f_path)

    def _load_seg_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/seg_models/efetivos_exo.pkl'
        return joblib.load(f_path)

    def _find_instances(self):
        _instances = []
        pattern = r"([cC]omiss[aã]o|[nN]atureza\s?[eE]special)"
        iterator = re.finditer(self._inst_rule, self._text, flags=self._flags)
        for _ in iterator:
            _m = re.findall(pattern, _[0], 0)
            if not _m:
                _instances.append(_.groups())
        return _instances

    def _props_names(self):
        return [
            'tipo',
            'nome',
            'matricula',
            'cargo_efetivo',
            'classe',
            'padrao',
            'carreira',
            'quadro',
            'SEI',
            'data',
            'pedido',
            'motivo',
            'SIAPE',
            'fundalamento_legal'
        ]

    def _rule_for_inst(self):
        start = r"(EXONERAR,\s?)"
        # body = r"((?:a\spedido,)?\s(?:[A-Z\\n\s]+),\s(?:matr[ií]cula\s(?:[0-9\.-])+)[,\sa-zA-Z0-9\\\/-]*)"
        body = r'((?:a\spedido,)?\s(?:[A-Z\\n\s]+),\s(?:matr[ií]cula\s(?:[0-9\.,X-])+)\s'+ \
            r'(?!.*\n?.*Cargo\sem\s+Comissao,|.*\n?.*Natureza\sEspecial,)[,\sa-zA-Z0-9\\\/-]*)'
        end = ""
        return start + body + end

    def _prop_rules(self):
        rules = {
                "nome": r"^(?:a\spedido,)?\s([A-Z\\n\s]+)",
                "matricula": r"matr[í|i]cula\s?n?o?\s([\s\S]*?)[,|\s]",
                "cargo_efetivo": r"matr[í|i]cula\s?n?o?\s[0-9]+,?([\sa-zA-Z]+)",
                "classe": r"matr[í|i]cula\s?n?o?\s[0-9]+,?[\sa-zA-Z]+[,\\n\s]+[eE]specialidade\s?([\sa-zA-Z]+)a\s?contar",
                "padrao": r"",
                "carreira": r"",
                "quadro": r"",
                "processo_SEI": r"SEI[a-z\s]*([0-9\-\/\n]+)",
                "data": r"a\scontar\sde\s([\s0-9\/]*)",
                "pedido": r"(a\spedido,)?\s(?:[A-Z\\n\s]+)",
                "motivo": r"",
                "matricula_SIAPE": r"",
                "fundamento_legal": r"nos\stermos\sdo[\n]?([a-zA-Z\s0-9\/]*)"}
        return rules
