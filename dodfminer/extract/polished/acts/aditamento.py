import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import re

from dodfminer.extract.polished.acts.base_contratos import AtosContrato

class Aditamento(AtosContrato):

  def __init__(self, file, backend = None, pipeline = None):
    super().__init__(file, backend=backend, pipeline=pipeline, model_path = '/models/modelo_aditamento_contratual.pkl')
    
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
