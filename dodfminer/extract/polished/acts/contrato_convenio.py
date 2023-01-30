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

class Contrato_Convenio():

  @property
  def acts_str(self):
    return self.atos_encontrados['texto']

  def __init__(self, file, pipeline = None):
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
    self.ner_extraction()
    if self.enablePostProcess: 
      self.post_process()
    else:
      self.data_frame = pd.DataFrame(self.predicted)

  def load(self):
    # Load model
    if self.pipeline is None:
      f_path = os.path.dirname(__file__)
      f_path += '/models/modelo_contrato_convenio.pkl'
      contrato_convenio_model = joblib.load(f_path)
      pipeline_CRF_default = Pipeline([('feat', feature_extractor()), ('crf', PipelineCRF(contrato_convenio_model))])
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
    atos_contrato_convenio = {
      'numero_dodf':[],
      'titulo':[],
      'texto':[]
    }
    df_atos_contrato_convenio = None

    principal_contrato = r'(?:CONTRATO)'

    regex_titulo_contrato = r'(?:(EXTRATO\sD[OE]\sCONTRATO)|(CONTRATO\sSIMPLIFICADO)|(CONTRATO\sPARA\sAQUISIÇÃO)|(^CONTRATO)'\
                            '|(EXTRATO\sD[OE]\sTERMO\sD[OE]\sCONTRATO\sNº\s)|(EXTRATO\sAO\sCONTRATO)|(CONTRATO\sDE\sPRESTAÇÃO\sDE\sSERVIÇOS\sNº)'\
                            '|(CONTRATO\sDE\sPATROCÍNIO)|(CONTRATO\sDE\sCONCESSÃO\sDE)|(^CONTRATO\sNº)|(^EXTRATOS\sDE\sCONTRATO[S]*))'

    principal_convenio = r'(?:(CONVÊNIO)|(CONVENIO))'

    regex_titulo_convenio = r'(?:(EXTRATO\sD[OE]\sCONVÊNIO)|(EXTRATO\sDE\sTERMO\sDE\sCONVÊNIO)|(CONVÊNIO\sSIMPLIFICADO)|(CONVÊNIO\sPARA\sAQUISIÇÃO)|(^CONVÊNIO)'\
                            '|(EXTRATO\sD[OE]\sTERMO\sD[OE]\sCONVÊNIO\sNº\s)|(EXTRATO\sAO\sCONVÊNIO)|(CONVÊNIO\sDE\sPRESTAÇÃO\sDE\sSERVIÇOS\sNº)'\
                            '|(CONVÊNIO\sDE\sPATROCÍNIO)|(CONVÊNIO\sDE\sCONCESSÃO\sDE)|(^CONVÊNIO\sNº)|(^EXTRATOS\sDE\sCONVÊNIO[S]*))'
    
    try:

      section_3 = file['json']['INFO']['Seção III']

      for orgao in section_3:
        for documento in section_3[orgao]:
          for ato in section_3[orgao][documento]:

            titulo = section_3[orgao][documento][ato]['titulo']

            if re.search(principal_contrato, titulo) is not None:
              if re.search(r'(?:ADITIVO)', titulo) is None:
                if re.search(regex_titulo_contrato, titulo) is not None:
                  if 'termo aditivo ao contrato' not in section_3[orgao][documento][ato]['texto'].lower():
                    atos_contrato_convenio['numero_dodf'].append(file['json']['nu_numero'])
                    atos_contrato_convenio['titulo'].append(titulo)
                    atos_contrato_convenio['texto'].append(re.sub(r'<[^>]*>', '', titulo + " " + section_3[orgao][documento][ato]['texto']))

            if re.search(principal_convenio, titulo) is not None:
              if re.search(r'(?:ADITIVO)', titulo) is None:
                if re.search(regex_titulo_convenio, titulo) is not None:
                  if 'termo aditivo ao con' not in section_3[orgao][documento][ato]['texto'].lower():
                    atos_contrato_convenio['numero_dodf'].append(file['json']['nu_numero'])
                    atos_contrato_convenio['titulo'].append(titulo)
                    atos_contrato_convenio['texto'].append(re.sub(r'<[^>]*>', '', titulo + " " + section_3[orgao][documento][ato]['texto']))

      df_atos_contrato_convenio = pd.DataFrame(atos_contrato_convenio)
    except KeyError:
      print(f"Chave 'Seção III' não encontrada no DODF {file['lstJornalDia']}!")
    print(f"Foram encontrados {len(atos_contrato_convenio['texto'])} atos de contrato/convênio")
    return df_atos_contrato_convenio

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
