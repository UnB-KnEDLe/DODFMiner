"""Regras regex para ato de Aviso de Julgamento em Licitações."""

import os
import joblib
from dodfminer.extract.polished.acts.base import Atos


class JulgamentoLicitacao(Atos):

    def __init__(self, file, backend):
        super().__init__(file, backend)

    def _act_name(self):
        return "Julgamento de Licitação"

    def _load_model(self):
        return None

    def _props_names(self):
        return ['Tipo do Ato', 'Id Ato', "DODF", "Data Ato/DODF", "Processo GDF/SEI", "Texto"]

    def _rule_for_inst(self):
        start = r"(AVISO(?:S)?\s+D[EO]\s+RESULTADO\s+D[EO]\s+JULGAMENTO|AVISO(?:S)?\s+D[EO]\s+JULGAMENTO)"
        body = r"([\s\S]*?<END_OF_BLOCK>"
        body1 = r"[\s\S]*?<END_OF_BLOCK>"
        body2 = r"[\s\S]*?<END_OF_BLOCK>"
        body3 = r"[\s\S]*?<END_OF_BLOCK>"
        body4 = r"[\s\S]*?<END_OF_BLOCK>"
        body5 = r"[\s\S]*?<END_OF_BLOCK>"
        end = r"[\s\S]*?<END_OF_BLOCK>)"
        return start + body + body1 + body2 + body3 + body4 + body5 + end

    def _prop_rules(self):
        rules = {"id_ato": r"",
                 "dodf": r"",
                 "data_dodf": r"Bras[[ií]lia(?:/?DF)?,?\s+(\d{2}\s+de+\s\w+\s+de\s+\d{4})",
                 "processo_SEI": r"""(?:(?:(?:P|p)rocesso(?:\s+)?(?:(?:()?SEI(?:)?))?(?:\s+)?(?:(?:no|n.o)?)?)|(?:P|p)rocesso:|(?:P|p)rocesso|Processo.|(?:P|p)rocesso\s+no|(?:P|p)rocesso\s+n.? ?o.?|(?:P|p)rocesso\s+no:|(?:P|p)rocesso\s+SEI\s+no:|(?:P|p)rocesso\s+SEI:|(?:P|p)rocesso\s+SEI-GDF:|(?:P|p)rocesso\s+SEI-GDF|(?:P|p)rocesso\s+SEI\s+no|(?:P|p)rocesso\s+SEI\s+n|(?:P|p)rocesso\s+SEI|(?:P|p)rocesso-\s+SEI|(?:P|p)rocesso\s+SEI\s+no.|(?:P|p)rocesso\s+(SEI)\s+no.|(?:P|p)rocesso\s+SEI.|(?:P|p)rocesso\s+(SEI-DF)\s+no.|(?:P|p)rocesso\s+SEI-GDF no|(?:P|p)rocesso\s+n|(?:P|p)rocesso\s+N|(?:P|p)rocesso\s+administrativo no|(?:P|p)rocesso\s+n:|PROCESSO: ?N?o?|PROCES-? ?SO|PROCESSO.|PROCESSO\s+no|PROCESSO\s+No|PROCESSO\s+N.o:?|PROCESSO\s+no.|PROCESSO\s+no:|PROCESSO\s+No:|PROCESSO\s+SEI\s+no:|PROCESSO\s+SEI:|PROCESSO\s+SEI|PROCESSO\s+SEI-GDF:|PROCESSO\s+SEI-GDF|PROCESSO\s+SEI\s+no|PROCESSO\s+SEI\s+No|PROCESSO\s+SEI\s+no.|PROCESSO\s+SEI.)((?:(?!\s\d{2}.\d{3}.\d{3}/\d{4}-\d{2}))(?:(?:\s)(?:(?:[\d.]+)|(?:[\d\s]+))[.-]?(?:(?:\d)|(?:[.\d\sSEI-|]+))(?:/|-
\b)(?:(?:(?:\d)+|(?:[\d\s]+)))?(?:-(?:(?:\d)+|(?:[\d\s]+)))?(?:-SECOM/DF|-?CEB|/CBMDF|F J Z B / D F)?))""",
                 "texto": r"([\s\S]+)",
                }
        return rules

