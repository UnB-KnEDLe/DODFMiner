import warnings
warnings.filterwarnings('ignore')

import sklearn_crfsuite
import pandas as pd
import numpy as np
import scipy.stats
import sklearn
import nltk
import joblib
import json
import re
import os

from sklearn_crfsuite.metrics import flat_classification_report, flat_f1_score
from sklearn.metrics import classification_report, make_scorer
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import train_test_split
from nltk.tokenize import word_tokenize
from sklearn_crfsuite import scorers

from dodfminer.extract.polished.backend.ner import JsonNER

class Aditamento():
  def __init__(self, file, backend):
    self.backend = backend
    self.model = None
    self.filename = file
    self.file = None
    self.atos_encontrados = []
    self.predicoes = []
    self.df = []
    # Inicializar fluxo
    self.flow()

  def flow(self):
    self.load()
    self.ner_extraction()
    self.post_process()
    
  def load(self):
    f_path = os.path.dirname(__file__)
    f_path += '/models/modelo_aditamento_contratual.pkl'
    self.model = joblib.load(f_path)
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

            if re.search(principal_aditivo, section_3[orgao][documento][ato]['titulo']) is not None:

              if re.search(regex_titulo_aditivo, section_3[orgao][documento][ato]['titulo']) is not None:
                atos_aditamento['numero_dodf'].append(file['json']['nu_numero'])
                atos_aditamento['titulo'].append(section_3[orgao][documento][ato]['titulo'])
                atos_aditamento['texto'].append(re.sub(r'<[^>]*>', '', section_3[orgao][documento][ato]['texto']))

              elif section_3[orgao][documento][ato]['titulo'] in titulos_termo_aditivo:
                if re.search(regex_texto_aditivo, section_3[orgao][documento][ato]['texto'].lower()) is not None:
                  atos_aditamento['numero_dodf'].append(file['json']['nu_numero'])
                  atos_aditamento['titulo'].append(section_3[orgao][documento][ato]['titulo'])
                  atos_aditamento['texto'].append(re.sub(r'<[^>]*>', '', section_3[orgao][documento][ato]['texto']))

      df_atos_aditamento = pd.DataFrame(atos_aditamento)
    except KeyError:
      print(f"Chave 'Seção III' não encontrada no DODF {file['lstJornalDia']}!")
    print(f"\nForam encontrados {len(atos_aditamento['texto'])} atos de aditamento")
    return df_atos_aditamento

  def ner_extraction(self):
    for t in self.atos_encontrados['texto']:
      pred = JsonNER.predict(t, self.model)
      self.predicoes.append(pred)

  # Montar dataframe com as predições e seus IOB's
  def post_process(self):
    for IOB, text, numdodf, titulo in zip(self.predicoes, self.atos_encontrados['texto'], self.atos_encontrados['numero_dodf'], self.atos_encontrados['titulo']):
      ent_dict = {
        'numero_dodf': '',
        'titulo': '',
        'text': '',
        # 'IOB': '',
      } 
      ent_dict['numero_dodf'] = numdodf
      ent_dict['titulo'] = titulo
      ent_dict['text'] = text
      # ent_dict['IOB'] = IOB
      entities = []
      text_split = word_tokenize(text)
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

      self.df.append(ent_dict)
    self.df = pd.DataFrame(self.df)
