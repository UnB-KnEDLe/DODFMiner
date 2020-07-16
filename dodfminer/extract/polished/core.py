"""Pure extractor core module.

This module contains the ActsExtractor class, which have all that is necessary to
extract a single act or all the acts from a DODF.

Usage Example::

    from dodfminer.extract.polished.core import ActsExtractor
    ActsExtractor.get_act_obj(ato_id, file, backend)

Acts Available and IDs
----------------------

"""

from dodfminer.extract.polished.acts.aposentadoria import Retirements, RetAposentadoria
from dodfminer.extract.polished.acts.nomeacao import NomeacaoComissionados, NomeacaoEfetivos
from dodfminer.extract.polished.acts.exoneracao import Exoneracao, ExoneracaoEfetivos
from dodfminer.extract.polished.acts.reversoes import Revertions
from dodfminer.extract.polished.acts.abono import AbonoPermanencia
from dodfminer.extract.polished.acts.substituicao import Substituicao
from dodfminer.extract.polished.acts.cessoes import Cessoes
from dodfminer.extract.polished.acts.sem_efeito_aposentadoria import SemEfeitoAposentadoria


_acts_ids = {"aposentadoria": Retirements,
             "reversoes": Revertions,
             "nomeacao": NomeacaoComissionados,
             "exoneracao": Exoneracao,
             "abono": AbonoPermanencia,
             "retificacoes": RetAposentadoria,
             "substituicao": Substituicao,
             "cessoes": Cessoes,
             "sem_efeito_aposentadoria": SemEfeitoAposentadoria,
             "efetivos_nome": NomeacaoEfetivos,
             "efetivos_exo": ExoneracaoEfetivos}
"""_acts_ids: All avaiable acts classes indexed by a given string name."""


class ActsExtractor:
    """Polished Extraction main class.

    All interactions with the acts needs to be done through this interface.
    This class handles all the requests to regex or ner extraction.

    Note:
        This class is static

    """

    @staticmethod
    def get_act_obj(ato_id, file, backend):
        """Extract a single act type from a single.

        Object format.

        Args:
            ato_id (string): The name of the act to extract.
            file (string): Path of the file.
            backend (string): Backend of act extraction, either regex or ner.

        Returns:
            An object of the desired act, already with extracted information.

        """
        return _acts_ids[ato_id](file, backend)

    @staticmethod
    def get_all_obj(file, backend):
        """Extract all acts types from a single DODF.

        Object format.

        Args:
            file (string): Path of the file.
            backend (string): Backend of act extraction, either regex or ner.

        Returns:
            An vector of objects of all the acts, already with extracted
            information.

        """
        res = {}
        for key in _acts_ids:
            res[key] = _acts_ids[key](file, backend)

        return res

    @staticmethod
    def get_act_df(ato_id, file, backend):
        """Extract a single act type from a single DODF.

        Dataframe format.

        Args:
            ato_id (string): The name of the act to extract.
            file (string): Path of the file.
            backend (string): Backend of act extraction, either regex or ner.

        Returns:
            An dataframe with extracted information, for the desired act.

        """
        return _acts_ids[ato_id](file, backend).data_frame

    @staticmethod
    def get_all_df(file, backend):
        """Extract all acts types from a single DODF.

        Dataframe format.

        Args:
            file (string): Path of the file.
            backend (string): Backend of act extraction, either regex or ner.

        Returns:
            An vector of dataframed with extracted information for all acts.

        """
        res = {}
        for key in _acts_ids:
            res[key] = _acts_ids[key](file, backend).data_frame

        return res
