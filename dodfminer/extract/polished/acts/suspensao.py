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

class Suspensao():

  @property
  def acts_str(self):
    if len(self.atos_encontrados) == 0: return []
    return self.atos_encontrados['texto'].tolist()

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

  def ner_extraction(self):
    pred = self.pipeline.predict(self.atos_encontrados['texto'])
    self.predicted = pred

  def post_process(self):
    for IOB, text, numdodf, titulo in zip(self.predicted, self.atos_encontrados['texto'], self.atos_encontrados['numero_dodf'], self.atos_encontrados['titulo']):
      ent_dict = {
        'numero_dodf': '',
        'titulo': '',
        'text': '',
      } 
      ent_dict['numero_dodf'] = numdodf
      ent_dict['titulo'] = titulo
      ent_dict['text'] = text
      entities = []

      if self.useDefault:
        text_split = nltk.word_tokenize(text)
      else:
        text_split = self.pipeline['pre-processing'].transform([text])[0]

      ent_concat = ('', '')
      aux = 0
      for ent, word in zip(IOB, text_split):
        if ent[0] == 'B':
          ent_concat = (ent[2:len(ent)], word)
        elif ent[0] == 'I':
          if aux != 0:
            ent_concat = (ent_concat[0], ent_concat[1] + ' ' + word)
          else:
            ent_concat = (ent[2:len(ent)], word)
        elif ent[0] == 'O':
          if ent_concat[1] != '':
            entities.append(ent_concat)
            ent_concat = ('', '')
              
        aux += 1
      for tup in entities:
        if tup[0] not in ent_dict:
          ent_dict[tup[0]] = tup[1]
        elif type(ent_dict[tup[0]]) != list:
          aux = []
          aux.append(ent_dict[tup[0]])
          aux.append(tup[1])
          ent_dict[tup[0]] = aux
        else:
          ent_dict[tup[0]].append(tup[1])

      self.data_frame.append(ent_dict)
    self.data_frame = pd.DataFrame(self.data_frame)

  # Montar dataframe com as predições e seus IOB's
  def highlight_dataframe(self):
    if len(self.atos_encontrados) == 0:
      return
    self.data_frame = []
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
