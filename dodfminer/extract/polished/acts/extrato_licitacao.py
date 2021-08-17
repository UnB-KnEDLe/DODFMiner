"""Regras regex para ato de Extrato de Licitação."""

import re
import os
import joblib
from dodfminer.extract.polished.acts.base import Atos


class ExtratoLicitacao(Atos):

    def __init__(self, file, backend):
        super().__init__(file, backend)

    def _regex_flags(self):
        return re.IGNORECASE

    def _act_name(self):
        return "Extrato de Licitação"

    # def _load_model(self):
    #     f_path = os.path.dirname(__file__)
    #     f_path += '/models/extrato_ner.pkl'
    #     return joblib.load(f_path)

    def _props_names(self):
        return ["Tipo do Ato", "Data DODF",
                "Processo GDF/SEI"]
# ["Tipo do Ato", "ID ato", "Órgão", "Data DODF",
# "Processo GDF/SEI", "Modalidade licitatória"]

    def _rule_for_inst(self):
        act = r'(EXTRATO\s+D[OE]\s+CONTRATO)'
        body = r"([\s\S]*?"
        end = r"<END_OF_BLOCK>){2}"
        return act + body + end

    def _prop_rules(self):
        rules = {"data_dodf": r"Bras[[ií]lia(?:/?DF)?,?\s+(\d{2}\s+de+\s\w+\s+de\s+\d{4})",
                 "processo_SEI": r'''(?:(?:(?:P|p)rocesso(?:\s+)?(?:(?:()?SEI(?:)?))?(?:\s+)?(?:(?:no|n.o)?)?)|(?:P|p)rocesso:|(?:P|p)rocesso|Processo.|(?:P|p)rocesso\s+no|(?:P|p)rocesso\s+n.? ?o.?|(?:P|p)rocesso\s+no:|(?:P|p)rocesso\s+SEI\s+no:|(?:P|p)rocesso\s+SEI:|(?:P|p)rocesso\s+SEI-GDF:|(?:P|p)rocesso\s+SEI-GDF|(?:P|p)rocesso\s+SEI\s+no|(?:P|p)rocesso\s+SEI\s+n|(?:P|p)rocesso\s+SEI|(?:P|p)rocesso-\s+SEI|(?:P|p)rocesso\s+SEI\s+no.|(?:P|p)rocesso\s+(SEI)\s+no.|(?:P|p)rocesso\s+SEI.|(?:P|p)rocesso\s+(SEI-DF)\s+no.|(?:P|p)rocesso\s+SEI-GDF no|(?:P|p)rocesso\s+n|(?:P|p)rocesso\s+N|(?:P|p)rocesso\s+administrativo no|(?:P|p)rocesso\s+n:|PROCESSO: ?N?o?|PROCES-? ?SO|PROCESSO.|PROCESSO\s+no|PROCESSO\s+No|PROCESSO\s+N.o:?|PROCESSO\s+no.|PROCESSO\s+no:|PROCESSO\s+No:|PROCESSO\s+SEI\s+no:|PROCESSO\s+SEI:|PROCESSO\s+SEI|PROCESSO\s+SEI-GDF:|PROCESSO\s+SEI-GDF|PROCESSO\s+SEI\s+no|PROCESSO\s+SEI\s+No|PROCESSO\s+SEI\s+no.|PROCESSO\s+SEI.)((?:(?!\s\d{2}.\d{3}.\d{3}/\d{4}-\d{2}))(?:(?:\s)(?:(?:[\d.]+)|(?:[\d\s]+))[.-]?(?:(?:\d)|(?:[.\d\sSEI-|]+))(?:/|-
\b)(?:(?:(?:\d)+|(?:[\d\s]+)))?(?:-(?:(?:\d)+|(?:[\d\s]+)))?(?:-SECOM/DF|-?CEB|/CBMDF|F J Z B / D F)?))''',
                 }
        return rules

# rules = {"tipo_ato": "Extrato",
#                  "id_ato": 12,
#                  "orgao": r"",
#                  "data_dodf": r"Bras[[ií]lia(?:/?DF)?,?\s+(\d{2}\s+de+\s\w+\s+de\s+\d{4})",
#                  "processo_SEI": r'''(?:(?:(?:P|p)rocesso(?:\s+)?(?:(?:()?SEI(?:)?))?(?:\s+)?(?:(?:no|n.o)?)?)|(?:P|p)rocesso:|(?:P|p)rocesso|Processo.|(?:P|p)rocesso\s+no|(?:P|p)rocesso\s+n.? ?o.?|(?:P|p)rocesso\s+no:|(?:P|p)rocesso\s+SEI\s+no:|(?:P|p)rocesso\s+SEI:|(?:P|p)rocesso\s+SEI-GDF:|(?:P|p)rocesso\s+SEI-GDF|(?:P|p)rocesso\s+SEI\s+no|(?:P|p)rocesso\s+SEI\s+n|(?:P|p)rocesso\s+SEI|(?:P|p)rocesso-\s+SEI|(?:P|p)rocesso\s+SEI\s+no.|(?:P|p)rocesso\s+(SEI)\s+no.|(?:P|p)rocesso\s+SEI.|(?:P|p)rocesso\s+(SEI-DF)\s+no.|(?:P|p)rocesso\s+SEI-GDF no|(?:P|p)rocesso\s+n|(?:P|p)rocesso\s+N|(?:P|p)rocesso\s+administrativo no|(?:P|p)rocesso\s+n:|PROCESSO: ?N?o?|PROCES-? ?SO|PROCESSO.|PROCESSO\s+no|PROCESSO\s+No|PROCESSO\s+N.o:?|PROCESSO\s+no.|PROCESSO\s+no:|PROCESSO\s+No:|PROCESSO\s+SEI\s+no:|PROCESSO\s+SEI:|PROCESSO\s+SEI|PROCESSO\s+SEI-GDF:|PROCESSO\s+SEI-GDF|PROCESSO\s+SEI\s+no|PROCESSO\s+SEI\s+No|PROCESSO\s+SEI\s+no.|PROCESSO\s+SEI.)((?:(?!\s\d{2}.\d{3}.\d{3}/\d{4}-\d{2}))(?:(?:\s)(?:(?:[\d.]+)|(?:[\d\s]+))[.-]?(?:(?:\d)|(?:[.\d\sSEI-|]+))(?:/|-
# \b)(?:(?:(?:\d)+|(?:[\d\s]+)))?(?:-(?:(?:\d)+|(?:[\d\s]+)))?(?:-SECOM/DF|-?CEB|/CBMDF|F J Z B / D F)?))''',
#                  "modalidade": r'(preg[ãõ\w]+\seletr[ô\w]+|concorrê\w+|tomad\w+\sd\w+\spre[ç\w]+|convite|concurs\w+|leil[ãõ\w]+|ordin[áa]ri\w+|globa\w+|estimativo|PE(?=\sn))'}
        