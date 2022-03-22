import re
import os
from typing import List, Match
import joblib
import pandas as pd
import numpy as np

from dodfminer.extract.polished.acts.base import Atos


def remove_crossed_words(string: str):
    '''
    Any hyfen followed by 1+ spaces are removed.
    '''
    return re.sub(r'-\s+', '', string)


LOWER_LETTER = r"[áàâäéèẽëíìîïóòôöúùûüça-z]"
UPPER_LETTER = r"[ÁÀÂÄÉÈẼËÍÌÎÏÓÒÔÖÚÙÛÜÇA-Z]"

DODF = r"(DODF|[Dd]i.rio\s+[Oo]ficial\s+[Dd]o\s+[Dd]istrito\s+[Ff]ederal)"

SIAPE = r"(?i:siape)\s*(?:n?.?)\s*(?P<siape>[-\d.Xx/\s]+)"
# SIAPE = r"(?i:siape)\s*(?:n?.?)\s*(?P<siape>[-\d.Xx/\s]+)"

MATRICULA = r"(?:matr.cul.|matr?[.]?\B)[^\d]+(?P<matricula>[-\d.XxZzYz/\s]+)"
# MATRICULA = r"(?i:matr.cul.|matr?[.]?\B)[^\d]+(?P<matricula>[-\d.XxZzYz/\s]+)"
MATRICULA_GENERICO = r"(?<![^\s])(?P<matricula>([-\d.XxZzYz/\s]{1,})[.-][\dXxYy][^\d])"
MATRICULA_ENTRE_VIRGULAS = r"(?<=[A-ZÀ-Ž]{3})\s*,\s+(?P<matricula>[-\d.XxZzYz/\s]{3,}?),"

SERVIDOR_NOME_COMPLETO = r"(servidor.?|empregad.)[^A-ZÀ-Ž]{0,40}(?P<name>[A-ZÀ-Ž][.'A-ZÀ-Ž\s]{6,}(?=[,]))"
# SERVIDOR_NOME_COMPLETO = r"(?i:servidor.?|empregad.)[^A-ZÀ-Ž]{0,40}(?P<name>[A-ZÀ-Ž][.'A-ZÀ-Ž\s]{6,}(?=[,]))"
NOME_COMPLETO = r"(?P<name>['A-ZÀ-Ž][.'A-ZÀ-Ž\s]{6,}(?=[,.:;]))"

PROCESSO_NUM = r"(?P<processo>[-0-9/.]+)"
INTERESSADO = rf"(?i:interessad.):\s*{NOME_COMPLETO}"
# INTERESSADO = r"(?i:interessad.):\s*{}".format(NOME_COMPLETO)
# INTERESSADO = r"(?i:interessad.):\s*" + NOME_COMPLETO

ONUS = r"(?P<onus>\b[oôOÔ](?i:nus)\b[^.]+[.])"
# ONUS = r"(?P<onus>\b[oôOÔ](?i:(nus))\b[^.]+[.])"


class Cessoes(Atos):
    '''
    Classe para atos de Cessoes
    '''

    _special_acts = ['matricula', 'cargo']

    def __init__(self, file, backend, debug=False, extra_search=True):
        self._debug = debug
        self._extra_search = extra_search
        # self._processed_text = remove_crossed_words(open(file).read())
        self._raw_matches = []
        super().__init__(file, backend)

    def _load_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/models/cessao.pkl'
        return joblib.load(f_path)

    def _load_seg_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/seg_models/cessao.pkl'
        return joblib.load(f_path)

    def _act_name(self):
        return "Cessoes"

    # def _load_model(self):
    #     f_path = os.path.dirname(__file__)
    #     f_path += '/models/cessoes_ner.pkl'
    #     return joblib.load(f_path)

    def get_expected_colunms(self) -> list:
        return list(self._prop_rules())

    def _props_names(self):
        return ["tipo"] + list(self._prop_rules())

    def _rule_for_inst(self):
        return (
            r"([Pp][Rr][Oo][Cc][Ee][Ss][Ss][Oo][^0-9/]{0,12})([^\n]+?\n){0,2}?"
            + r"[^\n]*?[Aa]\s*[Ss]\s*[Ss]\s*[Uu]\s*[Nn]\s*[Tt]\s*[Oo]\s*:?\s*\bCESS.O\b"
            + r"([^\n]*\n){0,}?[^\n]*?(?=(?P<look_ahead>PROCESSO|Processo:|PUBLICAR|pertinentes[.]|autoridade cedente|"
            + r"(?i:publique-se)" + "))"
        )

    def _prop_rules(self):
        return {
            'nome': SERVIDOR_NOME_COMPLETO,
            'matricula': MATRICULA,
            'cargo_efetivo': "",
            'classe': "",
            'padrao': "",
            'orgao_cedente': "",
            'orgao_cessionario': "",
            'onus': ONUS,
            'fundamento legal': "",
            'processo_SEI': rf"[^0-9]+?{PROCESSO_NUM}",
            'vigencia': "",
            'matricula_SIAPE': SIAPE,
            'cargo_orgao_cessionario': r",(?P<cargo>[^,]+)",
            'simbolo': "",
            'hierarquia_lotacao': "",
        }

    def _find_instances(self) -> List[Match]:
        """Returns list of re.Match objects found on `self._text_no_crosswords`.

        Return:
            a list with all re.Match objects resulted from searching for
        """

        self._raw_matches = list(
            re.finditer(self._inst_rule, self._text, flags=self._flags)
            # Makes difficult to mark XML later despite improving results.
            # re.finditer(self._inst_rule, self._processed_text, flags=self._flags)
        )
        list_matches = [i.group() for i in self._raw_matches]
        if self._debug:
            print("DEBUG:", len(list_matches), 'matches')
        return list_matches

    def _get_special_acts(self, lis_matches):
        for i, match in enumerate(self._raw_matches):
            act = match.group()
            matricula = re.search(MATRICULA, act) or \
                re.search(MATRICULA_GENERICO, act) or \
                re.search(MATRICULA_ENTRE_VIRGULAS, act)

            nome = re.search(self._rules['nome'], act)
            if matricula and nome:
                offset = matricula.end()-1 if 0 <= (matricula.start() - nome.end()) <= 5 \
                    else nome.end() - 1
                cargo, = self._find_prop_value(
                    r",(?P<cargo>[^,]+)", act[offset:])
            else:
                cargo = np.nan

            lis_matches[i]['matricula'] = matricula.group('matricula') if matricula \
                else np.nan
            lis_matches[i]['cargo'] = cargo

    def _find_prop_value(self, rule, act):
        """Returns named group, or the whole match if no named groups
                are present on the match.
        Args:
            match: a re.Match object
        Returns: content of the unique named group found at match,
            the whole match if there are no groups at all or raise
            an exception if there are more than two groups.
        """
        match = re.search(rule, act, flags=self._flags)

        if match:
            keys = list(match.groupdict().keys())
            if len(keys) == 0:
                return match.group()
            if len(keys) > 1:
                raise ValueError(
                    "Named regex must have AT MOST ONE NAMED GROUP.")
            if self._debug:
                print('key: ', keys[0])
            return (match.group(keys[0]),)
        return np.nan

    def _extract_props(self):
        acts = []

        for raw in self._raw_acts:
            act = self._regex_props(raw)
            # Merge act props with standard props
            acts.append(self.add_standard_props(act, capitalize=True))
        if self._extra_search:
            self._get_special_acts(acts)
        return acts

    def _regex_instances(self) -> List[Match]:
        found = self._find_instances()
        self._acts_str = found.copy()
        return found

    def _build_dataframe(self):
        """Create a dataframe with the extracted proprieties.

        Returns:
            The dataframe created
        """
        self._columns = list(self._prop_rules().keys()) + self._standard_props_names(capitalize=True)

        return (pd.DataFrame() if not self._acts else
                pd.DataFrame(self._acts, columns=self._columns))
