import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import re

from dodfminer.extract.polished.acts.base_contratos import AtosContrato

class Contrato(AtosContrato):

  def __init__(self, file, backend = None, pipeline = None):
    super().__init__(file, backend=backend, pipeline=pipeline, model_path = '/models/modelo_contrato_convenio.pkl')

  def segment(self, file):
    atos_contrato = {
      'numero_dodf':[],
      'titulo':[],
      'texto':[]
    }
    df_atos_contrato = None
    regex_contrato = r'(?:(EXTRATO\sD[OE]\sCONTRATO)|(CONTRATO\sSIMPLIFICADO)|(CONTRATO\sPARA\sAQUISIÇÃO)|(^CONTRATO)'\
                            '|(EXTRATO\sD[OE]\sTERMO\sD[OE]\sCONTRATO\sNº\s)|(EXTRATO\sAO\sCONTRATO)|(CONTRATO\sDE\sPRESTAÇÃO\sDE\sSERVIÇOS\sNº)'\
                            '|(CONTRATO\sDE\sPATROCÍNIO)|(CONTRATO\sDE\sCONCESSÃO\sDE)|(^CONTRATO\sNº)|(^EXTRATOS\sDE\sCONTRATO[S]*))'
    
    try:
      section_3 = file['json']['INFO']['Seção III']
      for orgao in section_3:
        for documento in section_3[orgao]:
          for ato in section_3[orgao][documento]:

            titulo = section_3[orgao][documento][ato]['titulo']

            if re.search(regex_contrato, titulo) is not None and re.search(r'(?:ADITIVO)', titulo) is None:
              atos_contrato['numero_dodf'].append(file['json']['nu_numero'])
              atos_contrato['titulo'].append(titulo)
              atos_contrato['texto'].append(re.sub(r'<[^>]*>', '', titulo + " " + section_3[orgao][documento][ato]['texto']))

      df_atos_contrato = pd.DataFrame(atos_contrato)
    except KeyError:
      print(f"Chave 'Seção III' não encontrada no DODF {file['lstJornalDia']}!")
    print(f"Foram encontrados {len(atos_contrato['texto'])} atos de contrato")
    return df_atos_contrato
  