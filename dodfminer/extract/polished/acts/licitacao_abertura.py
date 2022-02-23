"""Regras regex para ato de Abertura de Licitação."""

import re
import os
import joblib
import pandas as pd

from dodfminer.extract.polished.acts.base import Atos


class AberturaLicitacao(Atos):
    '''
    Classe para Abertura de Licitação
    '''

    def __init__(self, file, backend):
        super().__init__(file, backend)

    def _regex_flags(self):
        return re.IGNORECASE

    # def _load_model(self):
    #     f_path = os.path.dirname(__file__)
    #     f_path += '/models/'
    #     return joblib.load(f_path)

    def _act_name(self):
        return "Abertura de Licitação"

    def _props_names(self):
        return [
            "Tipo do Ato",
            "numero_licitacao",
            "nome_responsavel",
            "data_escrito",
            "objeto",
            "modalidade_licitacao",
            "processo_GDF",
            "valor",
            "data_abertura",
            "uasg",
            "sistema_compra",
            "tipo_objeto",
            "texto"
        ]

    def _rule_for_inst(self):
        start = r""
        body = r""
        end = r""

        return start + body + end

    def _prop_rules(self):
        rules = {
            "numero_licitacao": r"",
            "nome_responsavel": r"",
            "data_escrito": r"",
            "objeto": r"",
            "modalidade_licitacao": r"",
            "processo_GDF": r"",
            "valor": r"",
            "data_abertura": r"",
            "uasg": r"",
            "sistema_compra": r"",
            "tipo_objeto": r"",
            "texto": r"([\s\S]+)",
        }
        return rules

    @classmethod
    def _preprocess(cls, text):
        return text

    def _regex_instances(self):
        results = DFA.extract_text(self._text)

        return results


class DFA: # pylint: disable=too-few-public-methods
    """ Classe que implementa um autômato finito determinístico

    Recebe um texto e returna uma lista com todos os atos de 
    Abertura de Licitação encontrados no texto
    """

    @classmethod
    def extract_text(cls, txt_string):
        txt_string = txt_string.split('\n')

        regex = r'(?:xxbcet\s+)?(?:AVISO\s+D[EO]\s+ABERTURA\s+D[EO]\s+LICITA[CÇ][AÃ]O|AVISO\s+D[EO]\s+ABERTURA|AVISO\s+D[EO]\s+LICITA[CÇ][AÃ]O|AVISO\s+D[EO]\s+PREG[AÃ]O\s+ELETR[OÔ]NICO)'
        regex_s = r'(?:xxbcet\s+)?(?:“?AVISOS?|“?EXTRATOS?|“?RESULTADOS?|“?SECRETARIA ?|“?SUBSECRETARIA ?|“?PREG[AÃ]O|“?TOMADA|“?COMISS[AÃ]O|“?DIRETORIA|“?ATO|“?DEPARTAMENTO ?|“?COORDENA[CÇ][AÃ]O)'

        abertura_licitacao_text = []
        ato = False

        i = 0
        while i != len(txt_string):
            if re.match(regex, txt_string[i]):
                abertura_licitacao_text.append(txt_string[i])
                ato = True
                while ato:
                    i += 1
                    if i == len(txt_string):
                        break
                    if re.match(regex_s, txt_string[i]) and ('xxbob' in txt_string[i-1] or('—' in txt_string[i-1] and 'xxbob' in txt_string[i-2])):
                        i -= 2
                        break
                    else:
                        abertura_licitacao_text[-1] += '\n' + txt_string[i]
            else:
                i+=1
        
        return abertura_licitacao_text
