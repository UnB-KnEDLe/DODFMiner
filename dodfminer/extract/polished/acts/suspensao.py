import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import re

from dodfminer.extract.polished.acts.base_contratos import AtosContrato

class Suspensao(AtosContrato):

  def __init__(self, file, backend = None, pipeline = None):
    super().__init__(file, backend=backend, pipeline=pipeline, model_path = '/models/modelo_suspensao.pkl')

  def segment(self, file):
    atos_suspensao = {
      'numero_dodf':[],
      'titulo':[],
      'texto':[]
    }
    df_atos_suspensao = None
    regex_suspensao = r'(?:AVISO\s+D[EO]\s+SUSPENS[AÃ]O\s+D[EO]\s+LICITA[CÇ][AÃ]O|AVISO\s+D[EO]\s+SUSPENS[AÃ]O)'
    
    try:
      section_3 = file['json']['INFO']['Seção III']
      for orgao in section_3:
        for documento in section_3[orgao]:
          for ato in section_3[orgao][documento]:

            titulo = section_3[orgao][documento][ato]['titulo']

            if re.search(regex_suspensao, titulo) is not None:
              atos_suspensao['numero_dodf'].append(file['json']['nu_numero'])
              atos_suspensao['titulo'].append(titulo)
              atos_suspensao['texto'].append(re.sub(r'<[^>]*>', '', titulo + " " + section_3[orgao][documento][ato]['texto']))

      df_atos_suspensao = pd.DataFrame(atos_suspensao)
    except KeyError:
      print(f"Chave 'Seção III' não encontrada no DODF {file['lstJornalDia']}!")
    return df_atos_suspensao
