import re
import os
import joblib
import pandas as pd
from typing import List, Match

from dodfminer.extract.polished.acts.base import Atos


def case_insensitive(s: str):
    """Returns regular expression similar to `s` but case careless.

    Note: strings containing characters set, as `[ab]` will be transformed to `[[Aa][Bb]]`.
        `s` is espected to NOT contain situations like that.
    Args:
        s: the stringregular expression string to be transformed into case careless
    Returns:
        the new case-insensitive string
    """

    return ''.join([c if not c.isalpha() else '[{}{}]'.format(c.upper(), c.lower()) for c in s])


def remove_crossed_words(s: str):
    """Any hyfen followed by 1+ spaces are removed.
    """
    return re.sub(r'-\s+', '', s)


LOWER_LETTER = r"[áàâäéèẽëíìîïóòôöúùûüça-z]"
UPPER_LETTER = r"[ÁÀÂÄÉÈẼËÍÌÎÏÓÒÔÖÚÙÛÜÇA-Z]"

DODF = r"(DODF|[Dd]i.rio\s+[Oo]ficial\s+[Dd]o\s+[Dd]istrito\s+[Ff]ederal)"

SIAPE = r"{}\s*(?:n?.?)\s*(?P<siape>[-\d.Xx/\s]+)".format(case_insensitive("siape"))
# SIAPE = r"(?i:siape)\s*(?:n?.?)\s*(?P<siape>[-\d.Xx/\s]+)"

MATRICULA = r"(?:matr.cul.|matr?[.]?\B)[^\d]+(?P<matricula>[-\d.XxZzYz/\s]+)"
# MATRICULA = r"(?i:matr.cul.|matr?[.]?\B)[^\d]+(?P<matricula>[-\d.XxZzYz/\s]+)"
MATRICULA_GENERICO = r"(?<![^\s])(?P<matricula>([-\d.XxZzYz/\s]{1,})[.-][\dXxYy][^\d])"
MATRICULA_ENTRE_VIRGULAS = r"(?<=[A-ZÀ-Ž]{3})\s*,\s+(?P<matricula>[-\d.XxZzYz/\s]{3,}?),"

SERVIDOR_NOME_COMPLETO = r"(servidor.?|empregad.)[^A-ZÀ-Ž]{0,40}(?P<name>[A-ZÀ-Ž][.'A-ZÀ-Ž\s]{6,}(?=[,]))"
# SERVIDOR_NOME_COMPLETO = r"(?i:servidor.?|empregad.)[^A-ZÀ-Ž]{0,40}(?P<name>[A-ZÀ-Ž][.'A-ZÀ-Ž\s]{6,}(?=[,]))"
NOME_COMPLETO = r"(?P<name>['A-ZÀ-Ž][.'A-ZÀ-Ž\s]{6,}(?=[,.:;]))"

PROCESSO_NUM = r"(?P<processo>[-0-9/.]+)"
INTERESSADO = r"{}:\s*{}".format(case_insensitive("interessad."), NOME_COMPLETO)
# INTERESSADO = r"(?i:interessad.):\s*{}".format(NOME_COMPLETO)
# INTERESSADO = r"(?i:interessad.):\s*" + NOME_COMPLETO

ONUS = r"(?P<onus>\b[oôOÔ]{}\b[^.]+[.])".format(case_insensitive("nus"))
# ONUS = r"(?P<onus>\b[oôOÔ](?i:(nus))\b[^.]+[.])"


class Cessoes(Atos):
    _special_acts = ['matricula', 'cargo']

    def __init__(self, file, backend, debug=False, extra_search=True):
        self._debug = debug
        self._extra_search = extra_search
        self._processed_text = remove_crossed_words(open(file).read())
        self._raw_matches = []
        super().__init__(file, backend)

    def _act_name(self):
        return "Cessoes"

    def _load_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/models/cessoes_ner.pkl'
        return joblib.load(f_path)

    def _props_names(self):
        return ["tipo"] + list(self._prop_rules())

    def _rule_for_inst(self):
        return (
            r"([Pp][Rr][Oo][Cc][Ee][Ss][Ss][Oo][^0-9/]{0,12})([^\n]+?\n){0,2}?"
            + r"[^\n]*?[Aa]\s*[Ss]\s*[Ss]\s*[Uu]\s*[Nn]\s*[Tt]\s*[Oo]\s*:?\s*\bCESS.O\b"
            + r"([^\n]*\n){0,}?[^\n]*?(?=(?P<look_ahead>PROCESSO|Processo:|PUBLICAR|pertinentes[.]|autoridade cedente|"
            + case_insensitive('publique-se') + "))"
            # + r'(?i:publique-se)' + "))"
        )

    def _prop_rules(self):
        return {
            'interessado': INTERESSADO,
            'nome': SERVIDOR_NOME_COMPLETO,
            'matricula': MATRICULA,
            'processo': r"[^0-9]+?{}".format(PROCESSO_NUM),
            # 'processo': r"[^0-9]+?" + PROCESSO_NUM,
            'onus': ONUS,
            'siape': SIAPE,
            'cargo': r",(?P<cargo>[^,]+)",
        }

    def _find_instances(self) -> List[Match]:
        """Returns list of re.Match objects found on `self._text_no_crosswords`.

        Return:
            a list with all re.Match objects resulted from searching for
        """

        self._raw_matches = list(
            re.finditer(self._inst_rule, self._processed_text, flags=self._flags)
        )
        l = [i.group() for i in self._raw_matches]
        if self._debug:
            print("DEBUG:", len(l), 'matches')
        return l

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
                cargo, = self._find_props(r",(?P<cargo>[^,]+)", act[offset:])
            else:
                cargo = "nan"

            lis_matches[i]['matricula'] = matricula.group('matricula') if matricula \
                                        else "nan"
            lis_matches[i]['cargo'] = cargo


    def _find_props(self, rule, act):
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
            elif len(keys) > 1:
                raise ValueError("Named regex must have AT MOST ONE NAMED GROUP.")
            if self._debug:
                print('key: ', keys[0])
            return match.group(keys[0]),
        else:
            return "nan"


    def _acts_props(self):
        acts = []
        for raw in self._raw_acts:
            act = self._act_props(raw)
            acts.append(act)
        if self._extra_search:
            self._get_special_acts(acts)
        return acts


    def _extract_instances(self) -> List[Match]:
        found = self._find_instances()
        self._acts_str = found.copy()
        return found
