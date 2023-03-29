import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import re

from dodfminer.extract.polished.acts.base_contratos import AtosContrato

class Contrato_Convenio(AtosContrato):

  def __init__(self, file, backend = None, pipeline = None):
    super().__init__(file, backend=backend, pipeline=pipeline, model_path = '/models/modelo_contrato_convenio.pkl')

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
    return df_atos_contrato_convenio
