"""
Pure extractor core module.

This module contains the ActsExtractor class, which have all that is necessary to
extract a single act or all the acts from a DODF.

Usage Example::

    from dodfminer.extract.polished.core import ActsExtractor
    ActsExtractor.get_act_obj(ato_id, file, backend)

"""

import multiprocessing
from typing import List, Dict
from dodfminer.extract.polished.create_xml import XMLFy

from dodfminer.extract.polished.acts.aposentadoria import Retirements, RetAposentadoria
from dodfminer.extract.polished.acts.base import Atos
from dodfminer.extract.polished.acts.nomeacao import NomeacaoComissionados, NomeacaoEfetivos
from dodfminer.extract.polished.acts.exoneracao import Exoneracao, ExoneracaoEfetivos
from dodfminer.extract.polished.acts.reversoes import Revertions
from dodfminer.extract.polished.acts.abono import AbonoPermanencia
from dodfminer.extract.polished.acts.substituicao import Substituicao
from dodfminer.extract.polished.acts.cessoes import Cessoes
from dodfminer.extract.polished.acts.sem_efeito_aposentadoria import SemEfeitoAposentadoria
from dodfminer.extract.polished.acts.contrato import Contratos
# Atos seção 3
from dodfminer.extract.polished.acts.aditamento import Aditamento
from dodfminer.extract.polished.acts.licitacao import Licitacao
from dodfminer.extract.polished.acts.suspensao import Suspensao
from dodfminer.extract.polished.acts.anulacao_revogacao import Anulacao_Revogacao
from dodfminer.extract.polished.acts.contrato_convenio import Contrato_Convenio

_acts_ids = {
    "aposentadoria": Retirements,
    "reversoes": Revertions,
    "nomeacao": NomeacaoComissionados,
    "exoneracao": Exoneracao,
    "abono": AbonoPermanencia,
    "retificacoes": RetAposentadoria,
    "substituicao": Substituicao,
    "efetivos_nome": NomeacaoEfetivos,
    "efetivos_exo": ExoneracaoEfetivos,
    "sem_efeito_aposentadoria": SemEfeitoAposentadoria,
    "cessoes": Cessoes,
    "contrato": Contratos,
}

_acts_sec3 = {
    "contrato_convenio": Contrato_Convenio,
    "aditamento": Aditamento,
    "licitacao": Licitacao,
    "suspensao": Suspensao,
    "anulacao_revogacao": Anulacao_Revogacao,
}

"""_acts_ids: All avaiable acts classes indexed by a given string name."""


class ExtractEntDFParallelArgs():
    """
    Class for arguments of parallel extraction
    """
    act_type: str
    file: str
    backend: str
    act: Atos

    def __init__(self, act_type: str, file: str, backend: str, act: Atos):
        self.act_type = act_type
        self.file = file
        self.act = act
        self.backend = backend

    def get_act_type(self):
        return self.act_type

    def set_act_type(self, act_type: str):
        self.act_type = act_type


class ActsExtractor:
    """Polished Extraction main class.

    All interactions with the acts needs to be done through this interface.
    This class handles all the requests to Regex or NER extraction.

    Note:
        This class is static.

    """

    @staticmethod
    def get_all_obj_sec3(file):
        """
        Extract a single act type from a single JSON DODF.

        Object format.

        Args:
            ato_id (string): The name of the act to extract.
            file (string): Path of the file.
            backend (string): Backend of act extraction, either Regex or NER.

        Returns:
            An object of the desired act, already with extracted information.

        """
        res = {}
        for key, act in _acts_sec3.items():
            a = act(file, "ner")
            res[key] = a.df.copy()

        return res

    @staticmethod
    def get_act_obj(ato_id, file, backend):
        """
        Extract a single act type from a single DODF.

        Object format.

        Args:
            ato_id (string): The name of the act to extract.
            file (string): Path of the file.
            backend (string): Backend of act extraction, either Regex or NER.

        Returns:
            An object of the desired act, already with extracted information.

        """
        return _acts_ids[ato_id](file, backend)

    @staticmethod
    def get_all_obj(file, backend):
        """
        Extract all act types from a single DODF object.

        Object format.

        Args:
            file (string): Path of the file.
            backend (string): Backend of act extraction, either Regex or NER.

        Returns:
            An vector of objects of all the acts with extracted
            information.

        """
        res = {}
        for key, act in _acts_ids.items():
            res[key] = act(file, backend)

        return res

    @staticmethod
    def get_all_obj_parallel(file, backend, processes=4):
        '''
        Extract all act types from a single DODF object in paralel.

        Object format.

        Args:
            file (string): Path of the file.
            backend (string): Backend of act extraction, either Regex or NER.

        Returns:
            An vector of objects of all the acts with extracted
            information.
        '''
        res = {}
        args: List[ExtractEntDFParallelArgs] = []
        for key, act in _acts_ids.items():
            argument = ExtractEntDFParallelArgs(key, file, backend, act)
            args.append(argument)

        with multiprocessing.Pool(processes=processes) as pool:
            response = pool.map(ActsExtractor.run_thread_wrap, args)
            for act in response:
                res[act['tipo']] = act['ato']

        return res

    @staticmethod
    def run_thread_wrap(argument: ExtractEntDFParallelArgs):
        return {'tipo': argument.act_type, 'ato': argument.act(argument.file, argument.backend)}

    @staticmethod
    def get_act_df(ato_id, file, backend):
        """
        Extract a single act type from a single DODF.

        Dataframe format.

        Args:
            ato_id (string): The name of the act to extract.
            file (string): Path of the file.
            backend (string): Backend of act extraction, either Regex or NER.

        Returns:
            A dataframe with extracted information, for the desired act.

        """
        return _acts_ids[ato_id](file, backend).data_frame

    @staticmethod
    def get_all_df(file, backend):
        """
        Extract all act types from a single DODF file.

        Dataframe format.

        Args:
            file (string): Path of the file.
            backend (string): Backend of act extraction, either regex or ner.

        Returns:
            A vector of dataframes with extracted information for all acts.

        """
        res = {}
        for key, act in _acts_ids.items():
            res[key] = act(file, backend).data_frame

        return res

    @staticmethod
    def get_all_df_parallel(file, backend, processes=4) -> Dict:
        """
        Extract all act types from a single DODF file in parallel.

        Dataframe format.

        Args:
            file (string): Path of the file.
            backend (string): Backend of act extraction, either regex or ner.

        Returns:
            A vector of dataframes with extracted information for all acts.

        """
        res = {}
        args: List[ExtractEntDFParallelArgs] = []
        for key, act in _acts_ids.items():
            argument = ExtractEntDFParallelArgs(key, file, backend, act)
            args.append(argument)

        with multiprocessing.Pool(processes=processes) as pool:
            response = pool.map(ActsExtractor.run_thread_wrap_ent, args)
            for act in response:
                res[act['tipo']] = act['dataframe']

        return res

    @staticmethod
    def run_thread_wrap_ent(arguments: ExtractEntDFParallelArgs):
        return {'tipo': arguments.act_type, 'dataframe': arguments.act(arguments.file, arguments.backend).data_frame}

    @staticmethod
    def get_xml(file, _, i):
        """
        Extract all act types from a single DODF in xml.

        Dataframe format.

        Args:
            file (string): Path of the file.
            backend (string): Backend of act extraction, either regex or ner.

        Returns:
            A vector of dataframes with extracted information for all acts.

        """
        res = XMLFy(file, _acts_ids, i)
        return res
