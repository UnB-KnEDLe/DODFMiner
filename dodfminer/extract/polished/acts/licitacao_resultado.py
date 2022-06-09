"""Regras regex para ato de Resultado de Licitação."""

import re
import os
import joblib
import pandas as pd

from dodfminer.extract.polished.acts.base import Atos


class ResultadoLicitacao(Atos):
    '''
    Classe para Resultado de Licitação
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
        return "Resultado de Licitação"

    def get_expected_colunms(self) -> list:
        return [
            "Tipo do Ato",
            "texto"
        ]

    def _props_names(self):
        return [
            "Tipo do Ato",
            "texto"
        ]

    def _rule_for_inst(self):
        start = r""
        body = r""
        end = r""

        return start + body + end

    def _prop_rules(self):
        rules = {
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
    """Classe que implementa um autômato finito determinístico

    Recebe um texto e returna uma lista com todos os atos de 
    Resultado de Licitação encontrados no texto 
    """

    @classmethod
    def clean_text_by_word(cls, text):
        a = "\n".join([l for l in text.split("\n") if l != ""])
        words = a.replace("\n", " ").split(" ")
        words = [w for w in words if w != ""]
        
        m_words = []

        for i in range(len(words)):
            word = words[i]

            if (word[-1] == "-") and (i+1)<len(words):
                word = word[:-1] + words[i+1]
                i += 1

            m_words.append(word)
        
        return re.sub('xxbcet ?|xxbcet ?|xxeob ?|xxbob ?|xxecet ?', '', " ".join(m_words).replace("\r", "").strip())


    @classmethod
    def extract_text(cls, txt_string):
        txt_string = txt_string.split('\n')

        # Atos no singular
        regex = r'(?:xxbcet\s+)?(?:AVISO\s+D[EO]\s+RESULTADO|RESULTADO\s+FINAL|RESULTADO\s+D[EO]\s+LICITA[CÇ][AÃ]O)'
        regex_s = r'(?:xxbcet\s+)?(?:“?AVISOS?|“?EXTRATOS?|“?RESULTADOS?|“?SECRETARIA ?|“?SUBSECRETARIA ?|“?PREG[AÃ]O|“?TOMADA|“?COMISS[AÃ]O|“?DIRETORIA|“?ATO|“?DEPARTAMENTO ?|“?COORDENA[CÇ][AÃ]O|“?ACADEMIA|“?CONCURSO|“?COMPANHIA|“?CONVITE|“?FUNDA[CÇ][AÃ]O|“?CONSELHO|“?SUBSCRETARIA|“?PROJETO|“?EDITAL)'

        resultado_licitacao_text = []
        ato = False

        i = 0
        while i != len(txt_string):
            if re.match(regex, txt_string[i]):
                resultado_licitacao_text.append(txt_string[i])
                ato = True
                while ato:
                    i += 1
                    if i == len(txt_string):
                        break
                    if re.match(regex_s, txt_string[i]) and ('xxbob' in txt_string[i-1] or('—' in txt_string[i-1] and 'xxbob' in txt_string[i-2])):
                        i -= 2
                        break
                    else:
                        resultado_licitacao_text[-1] += '\n' + txt_string[i]
            else:
                i+=1

        # Atos no plural
        regex = r'(?:xxbcet\s+)?(?:RESULTADOS\s+FINAL|RESULTADOS\s+FINAIS|AVISOS\s+D[EO]\s+RESULTADO|AVISOS\s+D[EO]\s+RESULTADOS|RESULTADOS\s+D[EO]\s+LICITA[CÇ][AÃ]O|RESULTADOS\s+D[EO]\s+LICITA[CÇ][OÕ]ES)'
        regex_s = r'(?:xxbcet\s+)?(?:“?AVISOS?|“?EXTRATOS?|“?RESULTADOS?|“?SECRETARIA ?|“?SUBSECRETARIA ?|“?TOMADA|“?COMISS[AÃ]O|“?DIRETORIA|“?ATO|“?DEPARTAMENTO ?|“?COORDENA[CÇ][AÃ]O|“?ACADEMIA|“?CONCURSO|“?COMPANHIA|“?CONVITE|“?FUNDA[CÇ][AÃ]O|“?CONSELHO|“?SUBSCRETARIA|“?PROJETO|“?EDITAL)'

        resultados_licitacao_text = []
        ato = False

        i = 0
        while i != len(txt_string):
            if re.match(regex, txt_string[i]):
                resultados_licitacao_text.append(txt_string[i])
                ato = True
                while ato:
                    i += 1
                    if i == len(txt_string):
                        break
                    if re.match(regex_s, txt_string[i]) and ('xxbob' in txt_string[i-1] or('—' in txt_string[i-1] and 'xxbob' in txt_string[i-2])):
                        i -= 2
                        break
                    else:
                        resultados_licitacao_text[-1] += '\n' + txt_string[i]
            else:
                i+=1
        
        for texto in resultados_licitacao_text:
            for ato in texto.split('xxbob'):
                if len(ato) < 55 or (ato[0] == '\n' and not ato[1].isupper() and ato[1] != 'x'):
                    if len(resultado_licitacao_text) > 0:
                        resultado_licitacao_text[-1] = resultado_licitacao_text[-1] + ato
                else:
                    resultado_licitacao_text.append(ato)

        for i in range(len(resultado_licitacao_text)):
            resultado_licitacao_text[i] = cls.clean_text_by_word(resultado_licitacao_text[i])
        
        return resultado_licitacao_text
