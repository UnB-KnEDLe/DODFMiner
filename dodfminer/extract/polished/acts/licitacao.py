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
      ent_dict['text'] = text
      entities = []

      if self.useDefault:
        text_split = nltk.word_tokenize(text)
        ent_dict['text'] = " ".join(text_split)
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

      ent_dict['text'] = re.sub(r'[\（\）\(\)]', '', ent_dict['text'])
      for e in ent_dict:

        if e != "numero_dodf" and e != 'titulo' and e != 'text':

          if type(ent_dict[e]) is not list:
            ent_dict[e] = re.sub(r'[\（\）\(\)]', '', ent_dict[e])
            idx = re.search(ent_dict[e], ent_dict['text'])

            if idx is not None:
              ent_dict[e] = {
                    "entity":ent_dict[e],
                    "start":idx.start(),
                    "end":idx.end()
                  }

            else:
              ent_dict[e] = ent_dict[e]

          else:
            new_list = []

            for word in ent_dict[e]:
              new_word = re.sub(r'[\（\）\(\)]', '', word)
              idx = re.search(new_word, ent_dict['text'])

              if idx is not None:
                new_list.append(
                  {
                    "entity":new_word,
                    "start":idx.start(),
                    "end":idx.end()
                  }
                )

              else:
                new_list.append(new_word)
            
            ent_dict[e] = new_list

      self.data_frame.append(ent_dict)
    self.data_frame = pd.DataFrame(self.data_frame)