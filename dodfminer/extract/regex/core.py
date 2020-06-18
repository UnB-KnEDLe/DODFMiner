from atos.aposentadoria import Retirements
from atos.reversoes import Revertions
from atos.nomeacao import NomeacaoComissionados
from atos.exoneracao import Exoneracao
from atos.abono import AbonoPermanencia
from atos.retificacoes import RetAposentadoria
from atos.substituicao import Substituicao
from atos.sem_efeito_aposentadoria import SemEfeitoAposentadoria
from atos.cessoes import Cessoes

_dict = {"aposentadoria": Retirements, "reversoes": Revertions, "nomeacao": NomeacaoComissionados,
         "exoneracao": Exoneracao, "abono": AbonoPermanencia, "retificacoes": RetAposentadoria,
         "substituicao": Substituicao, "sem_efeito_aposentadoria": SemEfeitoAposentadoria,
         "cessoes": Cessoes}

class Regex:

    @staticmethod
    def get_act_obj(ato_id, file):
        return _dict[ato_id](file)

    @staticmethod
    def get_all_obj(file):
        res = {}
        for key in _dict:
            res[key] = _dict[key](file)
    
        return res

    @staticmethod
    def get_act_df(ato_id, file):
        return _dict[ato_id](file).data_frame
    
    @staticmethod
    def get_all_df(file):
        res = {}
        for key in _dict:
            res[key] = _dict[key](file).data_frame
    
        return res