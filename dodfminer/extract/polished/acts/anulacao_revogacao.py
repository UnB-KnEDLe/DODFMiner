import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import re

from dodfminer.extract.polished.acts.base_contratos import AtosContrato

class Anulacao_Revogacao(AtosContrato):

  def __init__(self, file, backend = None, pipeline = None):
    super().__init__(file, backend=backend, pipeline=pipeline, model_path = '/models/modelo_anulacao_revogacao.pkl')

  def segment(self, file):
    atos_anulacao_revogacao = {
      'numero_dodf':[],
      'titulo':[],
      'texto':[]
    }
    df_atos_anulacao_revogacao = None
    regex_anulacao_revogacao = r'(?:AVISO\s+D[EO]\s+REVOGA[CÇ][AÃ]O\s+D[EO]\s+LICITA[CÇ][AÃ]O|AVISO\s+D[EO]\s+REVOGA[CÇ][AÃ]O|AVISO\s+D[EO]\s+ANULA[CÇ][AÃ]O\s+D[EO]\s+LICITA[CÇ][AÃ]O|AVISO\s+D[EO]\s+ANULA[CÇ][AÃ]O)'
    
    try:
      section_3 = file['json']['INFO']['Seção III']
      for orgao in section_3:
        for documento in section_3[orgao]:
          for ato in section_3[orgao][documento]:

            titulo = section_3[orgao][documento][ato]['titulo']

            if re.search(regex_anulacao_revogacao, section_3[orgao][documento][ato]['titulo']) is not None:
              atos_anulacao_revogacao['numero_dodf'].append(file['json']['nu_numero'])
              atos_anulacao_revogacao['titulo'].append(titulo)
              atos_anulacao_revogacao['texto'].append(re.sub(r'<[^>]*>', '', titulo + " " + section_3[orgao][documento][ato]['texto']))

      df_atos_anulacao_revogacao = pd.DataFrame(atos_anulacao_revogacao)
    except KeyError:
      print(f"Chave 'Seção III' não encontrada no DODF {file['lstJornalDia']}!")
    return df_atos_anulacao_revogacao