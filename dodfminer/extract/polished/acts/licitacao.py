"""Regras regex para ato de Aviso de Licitação."""

import re
import os
import joblib
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
import numpy as np

from dodfminer.extract.polished.acts.base import Atos
from dodfminer.extract.polished.backend.ner import ActNER


class AvisoLicitacao(ActNER):
    '''
    Classe para Aviso de Licitação
    '''

    def __init__(self, arq, backend):
        self._acts = []
        self._file_name = arq
        self._model = self._load_model()
        self.data_frame = self.process()

    def _load_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/models/licitacao.pkl'
        return joblib.load(f_path)

    def _load_arq(self, arq):
        with open(arq, "r", encoding='utf-8') as file:
            text = file.read()
            file.close()
        return text

    def process(self):
        text_list = self._load_arq(self._file_name)
        self.sents = DFA.extract_text(text_list)   # lista de textos
        if not self.sents:
            return pd.DataFrame()

        for sent in self.sents:
            predicted = self._prediction(sent)  # lista com cada objeto predito
            self._acts.append(self.add_standard_props(predicted))

        return self._build_dataframe() 

    def _prediction(self, sent):
        """Predict classes for a single act.

        Args:
            act (string): Full act

        Returns:
            A dictionary with the proprieties and its
            predicted value.
        """
        act = self._preprocess(sent)    # lista de palavras tokenizadas
        features = self._get_features(act)  # lista de dicionarios que contem cada feature
        pred = self._model.predict_single(features) # lista com cada objeto predito
        self.dict_pred = self.predictions_dict(act, pred)   # dicionario com o resultado
        return self.dict_pred

    def _build_dataframe(self):
        """Create a dataframe with the extracted proprieties.

        Returns:
            The dataframe created
        """
        data_frame = pd.DataFrame.from_dict(self._acts)
        data_frame.columns = [x.capitalize()
                              for x in data_frame.columns]
        self._check_cols(data_frame.columns)
        return data_frame.drop('Iob', axis=1)
    
    def _standard_props(self):
        act = {}

        file = self._file_name.split('/')[-1] if self._file_name else None
        match = re.search(r'(\d+\-\d+\-\d+)',file) if file else None
        file_split = file.split() if file else None

        act['DODF_Fonte_Arquivo'] = file.replace('.txt', '.pdf') if file else None
        act['DODF_Fonte_Data'] = match.group(1).replace('-', '/') if match else None
        act['DODF_Fonte_Numero'] = file_split[1] if file_split and len(file_split)>=2 else None

        return act

    def add_standard_props(self, act, capitalize=False):
        standard_props = self._standard_props()

        if capitalize:
            standard_props = {(key.capitalize()):val for key, val in standard_props.items()}

        act = {**act, **(standard_props)}
        return act

    def _check_cols(self, columns: list) -> None:
        '''
            Check if dataframe columns are the expected ones
            Raises:
                NotImplementedError: Child class needs to overwrite this method.

        '''
        for col in self.get_expected_colunms():
            if col not in columns:
                raise KeyError(f'Key not present in dataframe -> {col}')
    
    def _preprocess(self, sentence):
        text = word_tokenize(sentence)
        return text

    def get_expected_colunms(self) -> list:
        return [
            "Modalidade_licitacao",
            "Num_licitacao",
            "Orgao_licitante",
            "Sistema_compras",
            "Obj_licitacao",
            "Valor_estimado",
            "Data_abertura",
            "Processo",
            "Nome_responsavel",
            "Codigo_sistema_compras",
            # "Texto" # comentar quando for usar ner
        ]

    def _get_features(self, sentence):
        """Create features for each word in act.
        Create a list of dict of words features to be used in the predictor module.
        Args:
            act (list): List of words in an act.
        Returns:
            A list with a dictionary of features for each of the words.
        """
        sent_features = []
        for i in range(len(sentence)):
            word_feat = {
                'word': sentence[i].lower(),
                'word[-3:]': sentence[i][-3:],
                'word[-2:]': sentence[i][-2:],
                'capital_letter': sentence[i][0].isupper(),
                'word_istitle': sentence[i].istitle(),
                'all_capital': sentence[i].isupper(),
                'word_isdigit': sentence[i].isdigit(),
                # Uma palavra antes
                'word_before': '' if i == 0 else sentence[i-1].lower(),
                'word_before_isdigit': '' if i == 0 else sentence[i-1].isdigit(),
                'word_before_isupper': '' if i == 0 else sentence[i-1].isupper(),
                'word_before_istitle': '' if i == 0 else sentence[i-1].istitle(),
                # Duas palavras antes
                'word_before2': '' if i in [0, 1] else sentence[i-2].lower(),
                'word_before_isdigit2': '' if i in [0, 1] else sentence[i-1].isdigit(),
                'word_before_isupper2': '' if i in [0, 1] else sentence[i-1].isupper(),
                'word_before_istitle2': '' if i in [0, 1] else sentence[i-1].istitle(),
                # Uma palavra depois
                'word_after': '' if i+1 >= len(sentence) else sentence[i+1].lower(),
                'word_after_isdigit': '' if i+1 >= len(sentence) else sentence[i+1].isdigit(),
                'word_after_isupper': '' if i+1 >= len(sentence) else sentence[i+1].isupper(),
                'word_after_istitle': '' if i+1 >= len(sentence) else sentence[i+1].istitle(),
                # Duas palavras depois
                'word_after2': '' if i+2 >= len(sentence) else sentence[i+2].lower(),
                'word_after_isdigit2': '' if i+2 >= len(sentence) else sentence[i+2].isdigit(),
                'word_after_isupper2': '' if i+2 >= len(sentence) else sentence[i+2].isupper(),
                'word_after_istitle2': '' if i+2 >= len(sentence) else sentence[i+2].istitle(),

                'BOS': i == 0,
                'EOS': i == len(sentence)-1
            }
            sent_features.append(word_feat)
        return sent_features

    def predictions_dict(self, act, prediction):
        """Create dictionary of proprieties.

        Create dictionary of tags to save predicted entities.

        Args:
            sentence (list): List of words and tokens in the act.
            prediction ([type]): The correspondent predicitons for each
                                 word in the sentence.

        Returns:
            A dictionary of the proprieties found.

        """
        dict_ato = {}
        for klass in self._model.classes_:
            if klass == 'O':
                continue
            dict_ato[klass[2:]] = []

        current = ''
        count = 0
        pred_start = 0

        for i,_ in enumerate(prediction):

            if prediction[i][0] == 'I':
                count += 1

            elif prediction[i][0] == 'B':
                pred_start = i

            elif prediction[i][0] == 'O' and pred_start:
                current = prediction[pred_start][2:]
                entidade = ' '.join(act[pred_start:i])
                dict_ato[current] = entidade
                pred_start = 0
                count = 0
            else:
                continue
           
        for key, val in dict_ato.items():
            if len(val) == 0:
                dict_ato[key] = np.nan
            elif len(val) == 1:
                dict_ato[key] = val[0]
        return dict_ato


class DFA: # pylint: disable=too-few-public-methods
    """ Classe que implementa um autômato finito determinístico

    Recebe um texto e returna uma lista com todos os atos de 
    Aviso de Licitação encontrados no texto
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
        licitacao_text = []
        # Atos no singular
        regex = r'(?:xxbcet\s+)?(?:AVISO\s+D[EO]\s+ABERTURA\s+D[EO]\s+LICITA[CÇ][AÃ]O|AVISO\s+D[EO]\s+ABERTURA|AVISO\s+D[EO]\s+LICITA[CÇ][AÃ]O|AVISO\s+D[EO]\s+PREG[AÃ]O\s+ELETR[OÔ]NICO)'
        regex_s = r'(?:xxbcet\s+)?(?:“?AVISOS?|“?EXTRATOS?|“?RESULTADOS?|“?SECRETARIA ?|“?SUBSECRETARIA ?|“?PREG[AÃ]O|“?TOMADA|“?COMISS[AÃ]O|“?DIRETORIA|“?ATO|“?DEPARTAMENTO ?|“?COORDENA[CÇ][AÃ]O|“?ACADEMIA|“?CONCURSO|“?COMPANHIA|“?CONVITE|“?FUNDA[CÇ][AÃ]O|“?CONSELHO|“?SUBSCRETARIA|“?PROJETO|“?EDITAL)'

        ato = False
        i = 0
        while i != len(txt_string):
            if re.match(regex, txt_string[i]):
                licitacao_text.append(txt_string[i])
                ato = True
                while ato:
                    i += 1
                    if i == len(txt_string):
                        break
                    if re.match(regex_s, txt_string[i]) and ('xxbob' in txt_string[i-1] or('—' in txt_string[i-1] and 'xxbob' in txt_string[i-2])):
                        i -= 2
                        break
                    else:
                        licitacao_text[-1] += '\n' + txt_string[i]
            else:
                i+=1

        # Atos no plural
        regex = r'(?:xxbcet\s+)?(?:AVISOS\s+D[EO]\s+ABERTURA\s+D[EO]\s+LICITA[CÇ][AÃ]O|AVISOS\s+D[EO]\s+ABERTURA|AVISOS\s+D[EO]\s+LICITA[CÇ][AÃ]O|AVISOS\s+D[EO]\s+PREG[AÃ]O\s+ELETR[OÔ]NICO|AVISOS\s+D[EO]\s+ABERTURA\s+D[EO]\s+LICITA[CÇ][OÕ]ES|AVISOS\s+D[EO]\s+LICITA[CÇ][OÕ]ES)'
        regex_s = r'(?:xxbcet\s+)?(?:“?AVISOS?|“?EXTRATOS?|“?RESULTADOS?|“?SECRETARIA ?|“?SUBSECRETARIA ?|“?TOMADA|“?COMISS[AÃ]O|“?DIRETORIA|“?ATO|“?DEPARTAMENTO ?|“?COORDENA[CÇ][AÃ]O|“?ACADEMIA|“?CONCURSO|“?COMPANHIA|“?CONVITE|“?FUNDA[CÇ][AÃ]O|“?CONSELHO|“?SUBSCRETARIA|“?PROJETO|“?EDITAL)'

        licitacoes_text = []
        ato = False

        i = 0
        while i != len(txt_string):
            if re.match(regex, txt_string[i]):
                licitacoes_text.append(txt_string[i])
                ato = True
                while ato:
                    i += 1
                    if i == len(txt_string):
                        break
                    if re.match(regex_s, txt_string[i]) and ('xxbob' in txt_string[i-1] or('—' in txt_string[i-1] and 'xxbob' in txt_string[i-2])):
                        i -= 2
                        break
                    else:
                        licitacoes_text[-1] += '\n' + txt_string[i]
            else:
                i+=1
        
        for texto in licitacoes_text:
            for ato in texto.split('xxbob'):
                if len(ato) < 55 or (ato[0] == '\n' and not ato[1].isupper() and ato[1] != 'x'):
                    if len(licitacao_text) > 0:
                        licitacao_text[-1] = licitacao_text[-1] + ato
                else:
                    licitacao_text.append(ato)

        for i in range(len(licitacao_text)):
            licitacao_text[i] = cls.clean_text_by_word(licitacao_text[i])

        return licitacao_text
