"""Regras regex para ato de Aposentadoria."""

import re
import os
import joblib
import pandas as pd
from dodfminer.extract.polished.acts.base import Atos


class Contratos(Atos):
     
    def __init__(self, file, backend):
        super().__init__(file, backend)

    def _regex_flags(self):
        return re.IGNORECASE

    def _load_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/models/efetivos_ret.pkl'
        return joblib.load(f_path)

    def _act_name(self):
        return "Contrato"

    def _props_names(self):
        return ["Tipo do Ato", "Objeto"]

    def _rule_for_inst(self):
        start = r"(EXTRATO DO CONTRATO\s)"
        body = r"([\s\S]*?"
        end = r"<EOB>)"
        return start + body + end

    def _prop_rules(self):
        regra_objeto = r"(?:OBJETO:)([\s\S]*?)[.]"

        rules = {'Objeto':regra_objeto
                 }
        return rules

    def _regex_instances(self):
        results = ContractExtractorREGEX.extract_text(self._text)

        return results

class ContractExtractorREGEX:
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
        
        base_str = txt_string

        contract_pattern_1 = r"(\nxx([a-z]{0,10})\sEXTRAT([A-Z]{0,3})\sD([A-Z]{0,3})\sCONTRAT([A-Z]{0,3}))"
        contract_pattern_2 = r"(\nxx([a-z]{0,10})\sEXTRAT([A-Z]{0,3})\sCONTRAT([A-Z]{0,3}))"

        contract_pattern = [contract_pattern_1, contract_pattern_2]
        contract_pattern = "|".join(contract_pattern)
        p_ext = re.compile(contract_pattern)

        block_pattern = r"(\nxx([a-z]{0,10})\s([A-ZÀ-Ú0-9º\/x\-\.\,\(\)\|\*&\s\']{5,}) xx([a-z]{0,10}))"
        block_pattern = block_pattern + "|" + contract_pattern
        p_blk = re.compile(block_pattern)

        nl_pattern = r"\n"
        p_nl = re.compile(nl_pattern)

        extracted_texts = cls._extract_text_blocks(base_str, p_ext, p_blk, p_nl)

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
            contract_texts = cls._clean_text(extracted_texts, start_page_patterns, end_page_patterns, middle_page_patterns)
        else:
            contract_texts = extracted_texts
            
        return contract_texts
    
    @classmethod
    def _extract_text_blocks(cls, base_str, contract_pattern, block_pattern, newline_pattern):
        matched_text = cls._row_list_regex(base_str, contract_pattern, block_pattern, newline_pattern)
        
        if matched_text != None:
            ext_blk_list = cls._mapped_positions_regex(matched_text)
            extracted_texts = cls._extract_texts_from_mapped_positions(ext_blk_list, base_str)
        else:
            extracted_texts = []

        return extracted_texts
    
    @classmethod
    def _clean_text(cls, ext_texts, start_page_patterns, end_page_patterns, middle_page_patterns):
        start_page_patterns = "|".join(start_page_patterns)
        middle_page_patterns = "|".join(middle_page_patterns)
        end_page_patterns = "|".join(end_page_patterns)

        page_patterns = [start_page_patterns, middle_page_patterns, end_page_patterns]
        page_patterns = "|".join(page_patterns)

        ext_texts = pd.Series(ext_texts).str.replace(page_patterns, "", regex=True)
        
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
        row_list = [re.findall(pattern_ext, text), re.finditer(pattern_ext, text), re.finditer(pattern_blk, text), re.finditer(pattern_nl, text)]

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

        for ia in mapped_position[0]:
            ia_b = ia[0]
            ia_e = ia[-1]
            index_ia_b = mapped_position[1].index(ia_b)
            index_ia_e = mapped_position[1].index(ia_e)

            if (index_ia_e + 1) <= (len(mapped_position[1])-1):
                ib = mapped_position[1][index_ia_e+1]
                extracted_text = mapped_text[ia_b:ib]
            else:
                extracted_text = mapped_text[ia_b:]

            extracted_texts.append(extracted_text)

        return extracted_texts

    @classmethod
    def _extract_titles_blocks(cls, mapped_page):
        ext = mapped_page[0].copy()
        blk = mapped_page[1].copy()
        nl = mapped_page[2].copy()

        tls = []

        for t in ext:
            tl = []
            tl.append(t)

            loop_title = True

            # Um título acaba quando o próximo bloco não é a próxima linha
            while loop_title:
                prox_blk_index = blk.index(t)+1
                prox_nl_index = nl.index(t)+1

                # Se o fim do documento não tiver sido alcançado
                if prox_blk_index < len(blk):
                    prox_blk = blk[prox_blk_index]
                    prox_nl = nl[prox_nl_index]

                    # Se a próxima linha for vista como um próximo bloco
                    if prox_blk == prox_nl:
                        t = prox_blk
                        tl.append(t)
                    else:
                        loop_title = False

                else:
                    loop_title = False

            tls.append(tl)

        return [tls, blk, nl]