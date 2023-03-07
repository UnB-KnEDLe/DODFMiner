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

class Anulacao_Revogacao(AtosContrato):

  def __init__(self, file, backend = None, pipeline = None):
    super().__init__(file, backend=backend, pipeline=pipeline)

  def load(self):
    # Load model
    if self.pipeline is None:
      f_path = os.path.dirname(__file__)
      f_path += '/models/modelo_anulacao_revogacao.pkl'
      anulacao_revogacao_model = joblib.load(f_path)
      pipeline_CRF_default = Pipeline([('feat', feature_extractor()), ('crf', PipelineCRF(anulacao_revogacao_model))])
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
    print(f"Foram encontrados {len(atos_anulacao_revogacao['texto'])} atos de anulação/revogação")
    return df_atos_anulacao_revogacao