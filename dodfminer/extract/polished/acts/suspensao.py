import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import joblib
import json
import re
import os

from dodfminer.extract.polished.acts.base_contratos import AtosContrato

from sklearn.pipeline import Pipeline
from dodfminer.extract.polished.backend.pipeline import feature_extractor, PipelineCRF

class Suspensao(AtosContrato):

  def __init__(self, file, backend = None, pipeline = None):
    super().__init__(file, backend=backend, pipeline=pipeline)
    
  def load(self):
    # Load model
    if self.pipeline is None:
      f_path = os.path.dirname(__file__)
      f_path += '/models/modelo_suspensao.pkl'
      suspensao_model = joblib.load(f_path)
      pipeline_CRF_default = Pipeline([('feat', feature_extractor()), ('crf', PipelineCRF(suspensao_model))])
      self.pipeline = pipeline_CRF_default
    else:
      self.useDefault = False
      try:
        self.pipeline['pre-processing'].transform(["test test"])
      except KeyError:
        self.enablePostProcess = False

    # Segmentation
    if self.filename[-5:] == '.json':
      with open(self.filename, 'r') as f:
        self.file = json.load(f)
        self.atos_encontrados = self.segment(self.file)
    else:
      pass

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
    print(f"Foram encontrados {len(atos_suspensao['texto'])} atos de suspensão")
    return df_atos_suspensao
