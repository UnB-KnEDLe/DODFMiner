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

class Aditamento():
  def __init__(self, file, pipeline = None):
    self.pipeline = pipeline
    self.filename = file
    self.file = None
    self.atos_encontrados = []
    self.predicted = []
    self.df = []
    self.enablePostProcess = True
    self.useDefault = True

    # Inicializar fluxo
    self.flow()

  def flow(self):
    self.load()
    self.ner_extraction()
    if self.enablePostProcess: 
      self.post_process()
    else:
      self.df = pd.DataFrame(self.predicted)
    
  def load(self):
    # Load model
    if self.pipeline is None:
      f_path = os.path.dirname(__file__)
      f_path += '/models/modelo_aditamento_contratual.pkl'
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
    atos_aditamento = {
      'numero_dodf':[],
      'titulo':[],
      'texto':[]
    }

    df_atos_aditamento = None

    principal_aditivo = r'(?:ADITIVO)'
    regex_titulo_aditivo = r'(?:(ADITIVO[S]*\s.*CONTRAT[OUALIS]*)|(CONTRATO[S]*\s.*ADITIVO[S]*)|(ADITIVO,\s.*CONTRATO))'
    regex_texto_aditivo = r'(?:(aditivo\sao\scontrato)|(espécie:\scontrato)|(termo\saditivo\s-\sao\scontrato))'

    titulos_termo_aditivo = [
      'EXTRATO DE TERMO ADITIVO',
      'EXTRATO DE ADITIVO',
      'EXTRATO DE TERMO ADITIVO (*)',
      'EXTRATOS DE TERMO ADITIVO',
      'EXTRATOS DE TERMOS ADITIVOS',
      'EXTRATO DO PRIMEIRO TERMO ADITIVO',
      'EXTRATO DE TERMO DE ADITIVO',
      'EXTRATO DE TERMOS ADITIVOS',
    ]
    
    try:
      section_3 = file['json']['INFO']['Seção III']

      for orgao in section_3:
        for documento in section_3[orgao]:
          for ato in section_3[orgao][documento]:

            titulo = section_3[orgao][documento][ato]['titulo']

            if re.search(principal_aditivo, titulo) is not None:
              if re.search(regex_titulo_aditivo, titulo) is not None:
                atos_aditamento['numero_dodf'].append(file['json']['nu_numero'])
                atos_aditamento['titulo'].append(titulo)
                atos_aditamento['texto'].append(re.sub(r'<[^>]*>', '', titulo + " " + section_3[orgao][documento][ato]['texto']))
              elif titulo in titulos_termo_aditivo:
                if re.search(regex_texto_aditivo, section_3[orgao][documento][ato]['texto'].lower()) is not None:
                  atos_aditamento['numero_dodf'].append(file['json']['nu_numero'])
                  atos_aditamento['titulo'].append(titulo)
                  atos_aditamento['texto'].append(re.sub(r'<[^>]*>', '', titulo + " " + section_3[orgao][documento][ato]['texto']))

      df_atos_aditamento = pd.DataFrame(atos_aditamento)
    except KeyError:
      print(f"Chave 'Seção III' não encontrada no DODF {file['lstJornalDia']}!")
    print(f"Foram encontrados {len(atos_aditamento['texto'])} atos de aditamento")
    return df_atos_aditamento

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
      self.df.append(ent_dict)
    self.df = pd.DataFrame(self.df)
