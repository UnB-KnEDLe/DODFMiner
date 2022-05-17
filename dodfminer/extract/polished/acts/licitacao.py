"""Regras regex para ato de Aposentadoria."""

import re
import os
import joblib
from dodfminer.extract.polished.acts.base import Atos


class Retirements(Atos):
    '''
    Classe para atos de licitação
    '''

    def __init__(self, file, backend):
        super().__init__(file, backend)

    def _regex_flags(self):
        return re.IGNORECASE

    def _load_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/models/licitacao.pkl'
        return joblib.load(f_path)

    def _load_seg_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/seg_models/licitacao.pkl'
        return joblib.load(f_path)

    def _act_name(self):
        return "Licitação"

    def get_expected_colunms(self) -> list:
        return [
            'Modalidade',
            'Processo',
            'Num_licitacao',
            'Orgao_licitante',
            'Sistema_compras',
            'Obj_licitacao',
            'Valor_estimado',
            'Data_abertura',
            'Nome_responsavel',
            'Codigo_sistema_compras',
            'Data_abertura',
        ]

    def _props_names(self):
        return [
            'Modalidade',
            'Processo',
            'Num_licitacao',
            'Orgao_licitante',
            'Sistema_compras',
            'Obj_licitacao',
            'Valor_estimado',
            'Data_abertura',
            'Nome_responsavel',
            'Codigo_sistema_compras',
            'Data_abertura',
        ]

