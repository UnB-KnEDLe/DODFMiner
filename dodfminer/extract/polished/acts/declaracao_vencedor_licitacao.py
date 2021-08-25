"""Regras regex para ato de Declaração de Vencedor em Licitações."""

import os
import joblib
from dodfminer.extract.polished.acts.base import Atos


class VencedorLicitacao(Atos):

    def __init__(self, file, backend):
        super().__init__(file, backend)

    def _act_name(self):
        return "Declaração de Vencedor"

    def _load_model(self):
        return None

    def _props_names(self):
        return ['Tipo do Ato', "DODF", "Data Ato/DODF", "Processo GDF/SEI", "Texto"]

    def _rule_for_inst(self):
        start = r"(AVISO(?:S)?\s+D[EO]\s+DECLARACAO\s+D[EO]\s+VENCEDOR|AVISO(?:S)?\s+D[EO]\s+RESULTADO)"
        body = r"([\s\S]*?"
        end = r"<END_OF_BLOCK>){3}"
        return start + body + end

    def _prop_rules(self):
        rules = {"dodf": r"",
                 "data_dodf": r"Bras[[ií]lia(?:/?DF)?,?\s+(\d{2}\s+de+\s\w+\s+de\s+\d{4})",
                 "processo_SEI": r"""(?:(?:(?:P|p)rocesso(?:\s+)?(?:(?:()?SEI(?:)?))?(?:\s+)?(?:(?:no|n.o)?)?)|(?:P|p)rocesso:|(?:P|p)rocesso|Processo.|(?:P|p)rocesso\s+no|(?:P|p)rocesso\s+n.? ?o.?|(?:P|p)rocesso\s+no:|(?:P|p)rocesso\s+SEI\s+no:|(?:P|p)rocesso\s+SEI:|(?:P|p)rocesso\s+SEI-GDF:|(?:P|p)rocesso\s+SEI-GDF|(?:P|p)rocesso\s+SEI\s+no|(?:P|p)rocesso\s+SEI\s+n|(?:P|p)rocesso\s+SEI|(?:P|p)rocesso-\s+SEI|(?:P|p)rocesso\s+SEI\s+no.|(?:P|p)rocesso\s+(SEI)\s+no.|(?:P|p)rocesso\s+SEI.|(?:P|p)rocesso\s+(SEI-DF)\s+no.|(?:P|p)rocesso\s+SEI-GDF no|(?:P|p)rocesso\s+n|(?:P|p)rocesso\s+N|(?:P|p)rocesso\s+administrativo no|(?:P|p)rocesso\s+n:|PROCESSO: ?N?o?|PROCES-? ?SO|PROCESSO.|PROCESSO\s+no|PROCESSO\s+No|PROCESSO\s+N.o:?|PROCESSO\s+no.|PROCESSO\s+no:|PROCESSO\s+No:|PROCESSO\s+SEI\s+no:|PROCESSO\s+SEI:|PROCESSO\s+SEI|PROCESSO\s+SEI-GDF:|PROCESSO\s+SEI-GDF|PROCESSO\s+SEI\s+no|PROCESSO\s+SEI\s+No|PROCESSO\s+SEI\s+no.|PROCESSO\s+SEI.)((?:(?!\s\d{2}.\d{3}.\d{3}/\d{4}-\d{2}))(?:(?:\s)(?:(?:[\d.]+)|(?:[\d\s]+))[.-]?(?:(?:\d)|(?:[.\d\sSEI-|]+))(?:/|-
\b)(?:(?:(?:\d)+|(?:[\d\s]+)))?(?:-(?:(?:\d)+|(?:[\d\s]+)))?(?:-SECOM/DF|-?CEB|/CBMDF|F J Z B / D F)?))""",
                 "texto": r"([\s\S]+)",
                }
        return rules

