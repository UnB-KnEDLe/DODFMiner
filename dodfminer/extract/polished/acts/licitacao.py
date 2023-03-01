import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import joblib
import nltk
import json
import re
import os

from sklearn.pipeline import Pipeline
from dodfminer.extract.polished.backend.pipeline import feature_extractor, PipelineCRF

class Licitacao():

  @property
  def acts_str(self):
    if len(self.atos_encontrados) == 0: return []
    return self.atos_encontrados['texto']

  def __init__(self, file, backend = None, pipeline = None):
    self.pipeline = pipeline
    self.filename = file
    self.file = None
    self.atos_encontrados = []
    self.predicted = []
    self.data_frame = []
    self.enablePostProcess = True
    self.useDefault = True

    # Inicializar fluxo
    self.flow()

  def flow(self):
    self.load()
    if len(self.atos_encontrados) == 0: 
      self.data_frame = pd.DataFrame()
      return 
    self.ner_extraction()
    if self.enablePostProcess: 
      self.post_process()
    else:
      self.data_frame = pd.DataFrame(self.predicted)
    
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

  def ner_extraction(self):
    pred = self.pipeline.predict(self.atos_encontrados['texto'])
    self.predicted = pred

  # Montar dataframe com as predições e seus IOB's
  def post_process(self):
    for IOB, text, numdodf, titulo in zip(self.predicted, self.atos_encontrados['texto'], self.atos_encontrados['numero_dodf'], self.atos_encontrados['titulo']):
      ent_dict = {
        'numero_dodf': '',
        'titulo': '',
        'text': '',
      } 
      ent_dict['numero_dodf'] = numdodf
      ent_dict['titulo'] = titulo
      ent_dict['text'] = ""

      if self.useDefault:
        text_split = nltk.word_tokenize(text)
      else:
        text_split = self.pipeline['pre-processing'].transform([text])[0]

      ent_list = []

      aux_text_token = []
      aux_text_string = ""

      i = 0
      while i < len(IOB):
          current_ent = {
              "name": [],
              "start": None,
              "end": None
          }

          if "B-" in IOB[i]:
              entity_name = IOB[i].replace("B-", "")
              aux_text_string = " ".join(aux_text_token).strip()
              aux_text_token.append(text_split[i])

              current_ent["start"] = len(aux_text_string) + 1
              current_ent["name"].append(text_split[i])

              i += 1

              while (i < len(IOB)) and ("I-" in IOB[i]):
                  current_ent["name"].append(text_split[i])
                  aux_text_token.append(text_split[i])

                  i += 1

              aux_text_string = " ".join(aux_text_token)
              current_ent["end"] = len(aux_text_string)
              current_ent["name"] = " ".join(current_ent["name"]).strip()
              ent_list.append(current_ent)
              if entity_name in ent_dict:
          
                new_list = [ent_dict[entity_name]]
     
                new_list.append(current_ent)
                ent_dict[entity_name] = new_list
              else:
                ent_dict[entity_name] = current_ent
          
          elif IOB[i] == 'O':
              aux_text_token.append(text_split[i])
              aux_text_string = " ".join(aux_text_token).strip()

          i += 1

      ent_dict['text'] = aux_text_string
      self.data_frame.append(ent_dict)
    self.data_frame = pd.DataFrame(self.data_frame)
