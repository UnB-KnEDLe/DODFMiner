"""Regras regex para ato de Revogação/Anulação de Licitação."""

import re
import os
import joblib
import pandas as pd

from dodfminer.extract.polished.acts.base import Atos


class RevogacaoAnulacaoLicitacao(Atos):
    '''
    Classe para Revogação/Anulação de Licitação
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
        return "Revogação/Anulação de Licitação"

    def get_expected_colunms(self) -> list:
        return [
            "Tipo do Ato",
            "numero_licitacao",
            "nome_responsavel",
            "data_escrito",
            "modalidade_licitacao",
            "processo_GDF",
            "classificacao",
            "texto"
        ]

    def _props_names(self):
        return [
            "Tipo do Ato",
            "numero_licitacao",
            "nome_responsavel",
            "data_escrito",
            "modalidade_licitacao",
            "processo_GDF",
            "classificacao",
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
            "modalidade_licitacao": r"",
            "processo_GDF": r"",
            "classificacao": r"",
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
    Revogação/Anulação de Licitação encontrados no texto
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
        regex = r'(?:xxbcet\s+)?(?:AVISO\s+D[EO]\s+REVOGA[CÇ][AÃ]O\s+D[EO]\s+LICITA[CÇ][AÃ]O|AVISO\s+D[EO]\s+REVOGA[CÇ][AÃ]O|AVISO\s+D[EO]\s+ANULA[CÇ][AÃ]O\s+D[EO]\s+LICITA[CÇ][AÃ]O|AVISO\s+D[EO]\s+ANULA[CÇ][AÃ]O)'
        regex_s = r'(?:xxbcet\s+)?(?:“?AVISOS?|“?EXTRATOS?|“?RESULTADOS?|“?SECRETARIA ?|“?SUBSECRETARIA ?|“?PREG[AÃ]O|“?TOMADA|“?COMISS[AÃ]O|“?DIRETORIA|“?ATO|“?DEPARTAMENTO ?|“?COORDENA[CÇ][AÃ]O|“?ACADEMIA|“?CONCURSO|“?COMPANHIA|“?CONVITE|“?FUNDA[CÇ][AÃ]O|“?CONSELHO|“?SUBSCRETARIA|“?PROJETO|“?EDITAL)'

        revogacao_anulacao_licitacao_text = []
        ato = False

        i = 0
        while i != len(txt_string):
            if re.match(regex, txt_string[i]):
                revogacao_anulacao_licitacao_text.append(txt_string[i])
                ato = True
                while ato:
                    i += 1
                    if i == len(txt_string):
                        break
                    if re.match(regex_s, txt_string[i]) and ('xxbob' in txt_string[i-1] or('—' in txt_string[i-1] and 'xxbob' in txt_string[i-2])):
                        break
                    else:
                        revogacao_anulacao_licitacao_text[-1] += '\n' + txt_string[i]
            else:
                i+=1
        
        # Atos no plural
        regex = r'(?:xxbcet\s+)?(?:AVISOS\s+D[EO]\s+REVOGA[CÇ][AÃ]O\s+D[EO]\s+LICITA[CÇ][AÃ]O|AVISOS\s+D[EO]\s+REVOGA[CÇ][AÃ]O|AVISOS\s+D[EO]\s+ANULA[CÇ][AÃ]O\s+D[EO]\s+LICITA[CÇ][AÃ]O|AVISOS\s+D[EO]\s+ANULA[CÇ][AÃ]O|AVISOS\s+D[EO]\s+REVOGA[CÇ][OÕ]ES\s+D[EO]\s+LICITA[CÇ][OÕ]ES|AVISOS\s+D[EO]\s+ANULA[CÇ][OÕ]ES\s+D[EO]\s+LICITA[CÇ][OÕ]ES|AVISOS\s+D[EO]\s+REVOGA[CÇ][OÕ]ES|AVISOS\s+D[EO]\s+ANULA[CÇ][OÕ]ES)'
        regex_s = r'(?:xxbcet\s+)?(?:“?AVISOS?|“?EXTRATOS?|“?RESULTADOS?|“?SECRETARIA ?|“?SUBSECRETARIA ?|“?TOMADA|“?COMISS[AÃ]O|“?DIRETORIA|“?ATO|“?DEPARTAMENTO ?|“?COORDENA[CÇ][AÃ]O|“?ACADEMIA|“?CONCURSO|“?COMPANHIA|“?CONVITE|“?FUNDA[CÇ][AÃ]O|“?CONSELHO|“?SUBSCRETARIA|“?PROJETO|“?EDITAL)'

        revogacoes_anulacoes_licitacao_text = []
        ato = False

        i = 0
        while i != len(txt_string):
            if re.match(regex, txt_string[i]):
                revogacoes_anulacoes_licitacao_text.append(txt_string[i])
                ato = True
                while ato:
                    i += 1
                    if i == len(txt_string):
                        break
                    if re.match(regex_s, txt_string[i]) and ('xxbob' in txt_string[i-1] or('—' in txt_string[i-1] and 'xxbob' in txt_string[i-2])):
                        break
                    else:
                        revogacoes_anulacoes_licitacao_text[-1] += '\n' + txt_string[i]
            else:
                i+=1
        
        for texto in revogacoes_anulacoes_licitacao_text:
            for ato in texto.split('xxbob'):
                if len(ato) < 55 or (ato[0] == '\n' and not ato[1].isupper() and ato[1] != 'x'):
                    if len(revogacao_anulacao_licitacao_text) > 0:
                        revogacao_anulacao_licitacao_text[-1] = revogacao_anulacao_licitacao_text[-1] + ato
                else:
                    revogacao_anulacao_licitacao_text.append(ato)

        for i in range(len(revogacao_anulacao_licitacao_text)):
            revogacao_anulacao_licitacao_text[i] = cls.clean_text_by_word(revogacao_anulacao_licitacao_text[i])

        return revogacao_anulacao_licitacao_text
