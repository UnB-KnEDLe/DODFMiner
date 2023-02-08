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

      self.df.append(ent_dict)
    self.df = pd.DataFrame(self.df)
