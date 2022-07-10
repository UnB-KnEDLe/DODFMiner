"""Regras regex para ato de Aditamento Contratual."""

import re
import os
import pandas as pd
import torch

import itertools
from nltk.tokenize import word_tokenize
from torch.nn.utils.rnn import pad_sequence

from dodfminer.extract.polished.acts.models.process_data import load_pkl, get_word2idx, get_char2idx, IOBES_tags
from dodfminer.extract.polished.acts.models.cnn_bilstm_crf import CNN_BiLSTM_CRF
from dodfminer.extract.polished.acts.base import Atos


class Aditamentos(Atos):
    '''
    Classe para aditamentos
    '''

    def __init__(self, file, backend):
        super().__init__(file, backend)

    def _regex_flags(self):
        return re.IGNORECASE

    def _load_model(self):
        self._check_model_files(['aditamento-cnn_bilstm_crf.pkl', 'aditamento-tag2idx.pkl', 'aditamento-word2idx.pkl', 'aditamento-char2idx.pkl'], self._name)
        self._check_embedding_files(['emb_cbow_s100.pkl'])

        f_path = os.path.dirname(__file__)        
        emb = load_pkl(os.path.join(f_path, 'embeddings', 'emb_cbow_s100.pkl'))
        self.tag2idx = load_pkl(os.path.join(f_path, 'prop_models', self._name, 'aditamento-tag2idx.pkl'))
        self.char2idx = load_pkl(os.path.join(f_path, 'prop_models', self._name, 'aditamento-char2idx.pkl'))
        self.word2idx = load_pkl(os.path.join(f_path, 'prop_models', self._name, 'aditamento-word2idx.pkl'))

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        model = CNN_BiLSTM_CRF(
            char_vocab_size=len(self.char2idx),
            pretrained_word_emb=emb,
            num_classes=len(self.tag2idx),
            device=device,
        )

        model = model.to(device)
        model.load_state_dict(torch.load(os.path.join(f_path, 'models', self._name, 'gold_aditamento_contratual-cnn_bilstm_crf.pkl')))

        return model

    def _process_data(self, text):
        sentence = word_tokenize(text)
        words = []
        
        if sentence:
            sentence = [word for word in itertools.chain(['<START>'], sentence, ['<END>'])]
            words = [[item for item in itertools.chain(['<START>'], [char for char in word], ['<END>'])] for word in sentence]

        sentence_ids = get_word2idx(sentence, self.word2idx)
        words_ids = get_char2idx(words, self.char2idx)
            
        return sentence, sentence_ids, words_ids

    def _get_features(self, sentence):
        words = sentence[1]
        sentence = sentence[0]

        sentence = torch.tensor(sentence)
        sentence = torch.unsqueeze(sentence, 0)

        words = pad_sequence([torch.tensor(w) for w in words], batch_first = True, padding_value=0)
        words = torch.unsqueeze(words, 0)
        
        mask = sentence != -1
        
        return sentence, words, mask

    def _predict_single(self, device, sentence, words, mask):
        sentence = sentence.to(device)
        words = words.to(device)
        mask = mask.to(device)

        pred, _ = self._model.decode(sentence, words, mask)
        iob_tags = IOBES_tags(pred.tolist(), self.tag2idx)
        
        return iob_tags[0]

    def _predictions_dict(self, sentence, prediction):
        sentence = sentence[1:-1]
        prediction = prediction[1:-1]
        
        tags_predicted = [w.split("-")[-1] for w in prediction]
        tags_positions = {t: [] for t in set(tags_predicted)}
        
        for i in range(len(tags_predicted)):
            tags_positions[tags_predicted[i]].append(sentence[i])
            
        tags_positions = {t: " ".join(tags_positions[t]) for t in tags_positions.keys()}
        tags_positions.pop("O")
        
        return tags_positions

    def _prediction(self, act):
        sentence, sentence_ids, words_ids = self._process_data(act)
        sentence_feats, words_feats, mask_feats = self._get_features([sentence_ids, words_ids])
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        predicted = self._predict_single(device, sentence_feats, words_feats, mask_feats)

        return self._predictions_dict(sentence, predicted)

    def _act_name(self):
        return "Aditamento"

    def get_expected_colunms(self) -> list:
        if self._backend == "regex":
            return [
                "Tipo do Ato",
                "CONTRATANTE",
                "ADITIVO",
                "CONTRATO",
                "OBJETO"
            ]
        return [
            "Num_aditivo",
            "Num_contrato",
            "Contratante",
            "Obj_aditivo"
            ]

    def _props_names(self):
        if self._backend == "regex":
            return [
                "Tipo do Ato",
                "CONTRATANTE",
                "ADITIVO",
                "CONTRATO",
                "OBJETO"
            ]
        return [
            "Num_aditivo",
            "Num_contrato",
            "Contratante",
            "Obj_aditivo"
            ]

    def _rule_for_inst(self):
        start = r"()"
        body = r"(EXTRATO D[O|E] CONTRATO\s[\s\S]*?"
        end = r"<EOB>)"

        return start + body + end

    def _prop_rules(self):
        rules = {
            "CONTRATANTE": r"[C|c][O|o][N|n][T|t][R|r][A|a][T|t][A|a][N|n][T|t][E|e][\s\S].*?(\d*[^;|.|]*)",
            "ADITIVO": r" (.*?)TERMO ADITIVO",
            "CONTRATO": r"EXTRATO D[E|O] CONTRATO[\s\S]*?(\d+\/\d{4})",
            "OBJETO": r"[O|o][B|b][J|j][E|e][T|t][O|o][\s\S].*?(\d*[^;|.|]*)"
        }
        return rules

    @classmethod
    def _preprocess(cls, text):
        text = text.replace(
            ':', ' : ').replace('``', ' ').replace("''", ' ')
        return text

    def _regex_instances(self):
        results = AditamentoExtratorREGEX.extract_text(self._text)

        return results

class AditamentoExtratorREGEX:  # pylint: disable=too-few-public-methods
    """Extract contract statements from a string and returns the contracts found in a list.

    Extracts contract statements from DODF dataframe through REGEX patterns.

    Note:
        This class is not constructable, it cannot generate objects.

    """

    @classmethod
    def extract_text(cls, txt_string):
        """Extract texts of contract statements from dataframe or file

        Args:
            txt_string: The string from where to extract the contracts.

        Returns:
            List with the contracts extracted from the string passed.
        """

        contract_pattern = r"(\nxx([a-z]{0,40})\s([-_ A-Za-z]{0,40})\sTERMO[S]{0,1} ADITIVO[S]{0,1})"
        p_ext = re.compile(contract_pattern)

        block_pattern = r"(\nxx([a-z]{0,10})\s([A-ZÀ-Ú0-9º\/x\-\.\,\(\)\|\*&\s\']{5,}) xx([a-z]{0,10}))"
        block_pattern = block_pattern + "|" + contract_pattern
        p_blk = re.compile(block_pattern)

        nl_pattern = r"\n"
        p_nl = re.compile(nl_pattern)

        extracted_texts = cls._extract_text_blocks(
            txt_string, p_ext, p_blk, p_nl)

        # Padrões de começo e fim de página abarcam apenas os padrões observados entre 2000 e 2021
        start_page_patterns = [r"\nPÁGINA\s([0-9]{1,5})", r"\nDIÁRIO\sOFICIAL\sDO\sDISTRITO\sFEDERAL",
                               r"\nNº(.+?)2([0-9]{3})", r"\nxx([a-z]{0,10}) Diário Oficial do Distrito Federal xx([a-z]{0,10})",
                               r"\nDiário Oficial do Distrito Federal"]

        end_page_patterns = [r"Documento assinado digitalmente conforme MP nº 2.200-2 de 24/08/2001, que institui a",
                             r"Infraestrutura de Chaves Públicas Brasileira ICP-Brasil",
                             r"Este documento pode ser verificado no endereço eletrônico",
                             r"http://wwwin.gov.br/autenticidade.html",
                             r"http://www.in.gov.br/autenticidade.html",
                             r"pelo código ([0-9]{15,18})",
                             r"\nDocumento assinado digitalmente, original em https://www.dodf.df.gov.br"]

        middle_page_patterns = [r"xx([a-z]{1,10}) ", r" xx([a-z]{1,10})", r"\n-\n",
                                r"xx([a-z]{1,10})", r"\n- -\n", r"\n- - -\n",
                                r"\n[\.\,\-\—]\n", r"— -"]

        if len(extracted_texts) > 0:
            contract_texts = cls._clean_text(
                extracted_texts, start_page_patterns, end_page_patterns, middle_page_patterns)
        else:
            contract_texts = extracted_texts

        return contract_texts

    @classmethod
    def _extract_text_blocks(cls, base_str, contract_pattern, block_pattern, newline_pattern):
        matched_text = cls._row_list_regex(
            base_str, contract_pattern, block_pattern, newline_pattern)

        if matched_text is not None:
            ext_blk_list = cls._mapped_positions_regex(matched_text)
            extracted_texts = cls._extract_texts_from_mapped_positions(
                ext_blk_list, base_str)
        else:
            extracted_texts = []

        return extracted_texts

    @classmethod
    def _clean_text(cls, ext_texts, start_page_patterns, end_page_patterns, middle_page_patterns):
        start_page_patterns = "|".join(start_page_patterns)
        middle_page_patterns = "|".join(middle_page_patterns)
        end_page_patterns = "|".join(end_page_patterns)

        page_patterns = [start_page_patterns,
                         middle_page_patterns, end_page_patterns]
        page_patterns = "|".join(page_patterns)

        ext_texts = pd.Series(ext_texts).str.replace(
            page_patterns, "", regex=True)

        ext_texts_list = []

        for text in ext_texts:
            ext_texts_list.append(cls._remove_empty_line(text))

        return ext_texts_list

    @classmethod
    def _remove_empty_line(cls, text):
        return "\n".join([line for line in text.split("\n") if line.strip() != ""])

    @classmethod
    def _row_list_regex(cls, text, pattern_ext, pattern_blk, pattern_nl):
        # Lista com as buscas por regex. O findall permite ver se no documento há pelo menos 1 extrato detectado
        row_list = [re.findall(pattern_ext, text), re.finditer(
            pattern_ext, text), re.finditer(pattern_blk, text), re.finditer(pattern_nl, text)]

        # Se findall não achou nenhum, então o documento não tem nada que interessa
        if len(row_list[0]) == 0:
            return None

        return row_list

    @classmethod
    def _mapped_positions_regex(cls, matched_text):
        # Mapeia as posições do que foi encontrado pelo regex
        # Lista de 2 dimensões: na primeira, de extrato; na segunda, de bloco

        a_ext = matched_text[1]
        a_blk = matched_text[2]
        a_nl = matched_text[3]

        a_ext_list = []
        a_blk_list = []
        a_nl_list = []

        for i in a_ext:
            a_ext_list.append(i.start())

        for i in a_blk:
            a_blk_list.append(i.start())

        for i in a_nl:
            a_nl_list.append(i.start())

        return [a_ext_list, a_blk_list, a_nl_list]

    @classmethod
    def _extract_texts_from_mapped_positions(cls, mapped_positions, mapped_text):
        extracted_texts = []

        mapped_position = cls._extract_titles_blocks(mapped_positions)

        for position_a in mapped_position[0]:
            ia_b = position_a[0]
            ia_e = position_a[-1]
            index_ia_e = mapped_position[1].index(ia_e)

            if (index_ia_e + 1) <= (len(mapped_position[1])-1):
                position_b = mapped_position[1][index_ia_e+1]
                extracted_text = mapped_text[ia_b:position_b]
            else:
                extracted_text = mapped_text[ia_b:]

            extracted_texts.append(extracted_text)

        return extracted_texts

    @classmethod
    def _extract_titles_blocks(cls, mapped_page):
        ext = mapped_page[0].copy()
        blk = mapped_page[1].copy()
        line = mapped_page[2].copy()

        tls = []

        for t_ext in ext:
            title = []
            title.append(t_ext)

            loop_title = True

            # Um título acaba quando o próximo bloco não é a próxima linha
            while loop_title:
                prox_blk_index = blk.index(t_ext)+1
                prox_line_index = line.index(t_ext)+1

                # Se o fim do documento não tiver sido alcançado, então:
                if prox_blk_index < len(blk):
                    prox_blk = blk[prox_blk_index]
                    prox_line = line[prox_line_index]

                    # Se a próxima linha for vista como um próximo bloco:
                    if prox_blk == prox_line:
                        t_ext = prox_blk
                        title.append(t_ext)
                    else:
                        loop_title = False

                else:
                    loop_title = False

            tls.append(title)

        return [tls, blk, line]