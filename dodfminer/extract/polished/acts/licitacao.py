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

class Licitacao(AtosContrato):

  def __init__(self, file, backend = None, pipeline = None):
    super().__init__(file, backend=backend, pipeline=pipeline)
    
  def load(self):
    # Load model
    if self.pipeline is None:
      f_path = os.path.dirname(__file__)
      f_path += '/models/modelo_licitacao.pkl'
      aditamento_model = joblib.load(f_path)
      pipeline_CRF_default = Pipeline([('feat', feature_extractor()), ('crf', PipelineCRF(aditamento_model))])
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
    atos_licitacao = {
      'numero_dodf':[],
      'titulo':[],
      'texto':[]
    }
    df_atos_licitacao = None
    regex_licitacao = r'(?:AVISO\s+D[EO]\s+ABERTURA\s+D[EO]\s+LICITA[CÇ][AÃ]O|AVISO\s+ABERTURA\s+D[EO]\s+LICITA[CÇ][AÃ]O|AVISO\s+D[EO]\s+LICITA[CÇ][AÃ]O|AVISO\s+D[EO]\s+PREG[AÃ]O\s+ELETR[OÔ]NICO|AVISOS\s+D[EO]\s+ABERTURA\s+D[EO]\s+LICITA[CÇ][AÃ]O|AVISOS\s+D[EO]\s+LICITA[CÇ][AÃ]O|AVISOS\s+D[EO]\s+PREG[AÃ]O\s+ELETR[OÔ]NICO|AVISOS\s+D[EO]\s+ABERTURA\s+D[EO]\s+LICITA[CÇ][OÕ]ES|AVISOS?\s+D[EO]\s+LICITA[CÇ][OÕ]ES)'
    
    try:
      section_3 = file['json']['INFO']['Seção III']
      for orgao in section_3:
        for documento in section_3[orgao]:
          for ato in section_3[orgao][documento]:

            titulo = section_3[orgao][documento][ato]['titulo']

            if re.search(regex_licitacao, titulo) is not None:
              atos_licitacao['numero_dodf'].append(file['json']['nu_numero'])
              atos_licitacao['titulo'].append(titulo)
              atos_licitacao['texto'].append(re.sub(r'<[^>]*>', '', titulo + " " + section_3[orgao][documento][ato]['texto']))

      df_atos_licitacao = pd.DataFrame(atos_licitacao)
    except KeyError:
      print(f"Chave 'Seção III' não encontrada no DODF {file['lstJornalDia']}!")
    print(f"Foram encontrados {len(atos_licitacao['texto'])} atos de licitação")
    return df_atos_licitacao
