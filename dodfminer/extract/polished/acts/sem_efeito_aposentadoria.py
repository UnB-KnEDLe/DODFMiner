import re
import os
from typing import List, Match
import joblib
import pandas as pd
import numpy as np
from dodfminer.extract.polished.acts.base import Atos


DODF = r"(DODF|[Dd]i.rio\s+[Oo]ficial\s+[Dd]o\s+[Dd]istrito\s+[Ff]ederal)"
_EDICAO_DODF = r"(\b(?i:suplement(o|ar)|extra|.ntegra))\b."
TIPO_EDICAO = r"\b(?P<tipo>(?i:extra(\sespecial)?|suplement(ar|o)))\b"
DODF_TIPO_EDICAO = DODF + r"(?P<tipo_edicao>.{0,50}?)" + _EDICAO_DODF

MONTHS = (
    r'(?i:janeiro|fevereiro|mar.o|abril|maio|junho|'
    r'julho|agosto|setembro|outubro|novembro|dezembro)'
)

FLEX_DATE = r"(?P<date>\d+\s+(?:de\s*)?" + MONTHS + \
    r"\s*(?:de\s*)?\d+|\d+[.]\d+[.]\d+|\d+[/]\d+[/]\d+)"

DODF_NUM = r"(?i:DODF|[Dd]i.rio [Oo]ficial [Dd]o [Dd]istrito [Ff]ederal)\s*[\w\W]{0,3}?(?i:n?(.mero|[.roº]{1,4})?[^\d]+?)(?P<num>\d+)"

DODF_DATE = DODF + r"[^\n\n]{0,50}?(?i:de\s?)?" + FLEX_DATE

SIAPE = r"(?i:siape)\s*(?i:n?.?)\s*[-\d.Xx/\s]"

MATRICULA = r"(?i:matr.cul.|matr?[.]?\B)[^\d]+(?P<matricula>[-\d.XxZzYz/\s]+)"

MATRICULA_GENERICO = r"(?<![^\s])(?P<matricula>([-\d.XxZzYz/\s]{1,})[.-][\dXxYy][^\d])"

MATRICULA_ENTRE_VIRGULAS = r"(?<=[A-ZÀ-Ž]{3})\s*,\s+([-\d.XxZzYz/\s]{3,}?),"

PAGE = r"((?i:p\.|p.ginas?|p.?gs?\.?\b)(?P<page_nums>.{0,}?)(?=[,;:]|\n|\s[A-Z]|$))"

SERVIDOR_NOME_COMPLETO = r"(?i:servidora?\b.{0,40}?)(?P<name>[A-ZÀ-Ž][.'A-ZÀ-Ž\s]{7,})"

NOME_COMPLETO = r"(?P<name>[.'A-ZÀ-Ž\s]{8,})"

LOWER_LETTER = r"[áàâäéèẽëíìîïóòôöúùûüça-z]"
UPPER_LETTER = r"[ÁÀÂÄÉÈẼËÍÌÎÏÓÒÔÖÚÙÛÜÇA-Z]"

PROCESSO_MATCH = r"(?i:processo):?[^\d]{0,50}?(?P<processo>\d[-0-9./\s]*\d(?!\d))"
TIPO_DOCUMENTO = r"(?i:portaria|ordem de servi.o|instru..o)"

EMPTY_MATCH = r'(?!x)x'


class SemEfeitoAposentadoria(Atos):
    '''
    Classe para atos que tornam aposentadoria sem efeito
    '''

    _special_acts = [
        'data_documento',
        'tipo_edicao',
        'numero_dodf',
        'pagina_dodf',
        'nome',
        'cargo_efetivo',
        'matricula',
    ]

    _BAD_MATCH_WORDS = [
        "AVERBAR",
        "NOMEAR",
        "CONCEDER",
        "EXONERAR",
        "DESAVERBAR",
        "APOSTILAR",
        "RETIFICAR",
    ]

    @classmethod
    def _pre_process_text(cls, text):
        # Make sure words splitted accross lines are joined together
        no_split_word = text.replace('-\n', '-')
        return no_split_word.replace('\n', ' ')

    # pylint: disable=too-many-arguments
    def __init__(self, file, backend, debug=False, extra_search=True,
                 nlp=None, max_length=2000):
        self._max_length = max_length
        self._debug = debug
        self._extra_search = extra_search
        # self._processed_text = self._pre_process_text(open(file).read())
        self._raw_matches = []
        self._nlp = nlp
        super().__init__(file, backend)

    def _load_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/models/sem_efeito_apo.pkl'
        return joblib.load(f_path)

    def _load_seg_model(self):
        f_path = os.path.dirname(__file__)
        f_path += '/seg_models/sem_efeito_apo.pkl'
        return joblib.load(f_path)

    def _act_name(self):
        return "Atos tornados sem efeito - aposentadoria"

    def get_expected_colunms(self) -> list:
        return self._props_names()

    def _props_names(self):
        return list(self._prop_rules())

    def _rule_for_inst(self):
        return (
            r"TORNAR SEM EFEITO"
            r"([^\n]+\n){0,10}?[^\n]*?"
            r"(tempo\sde\sservi.o|aposentadoria|aposentou|([Dd][Ee][Ss])?[Aa][Vv][Ee][Rr][Bb][Aa]..[Oo]|(des)?averb(ar?|ou))"
            r"[\d\D]{0,500}?[.]\s+"
            r"(?=[A-Z]{3})"
        )

    def _prop_rules(self):
        return {
            'tipo_documento': TIPO_DOCUMENTO,
            'numero_documento': EMPTY_MATCH,
            'data_documento': EMPTY_MATCH,
            'numero_dodf': EMPTY_MATCH,
            'data_dodf': DODF_DATE,
            'pagina_dodf': EMPTY_MATCH,
            'nome': EMPTY_MATCH,
            'matricula': EMPTY_MATCH,
            'matricula_SIAPE': EMPTY_MATCH,
            'cargo_efetivo': EMPTY_MATCH,
            'classe': EMPTY_MATCH,
            'padrao': EMPTY_MATCH,
            'quadro': EMPTY_MATCH,
            'orgao': EMPTY_MATCH,
            'processo_SEI': PROCESSO_MATCH,
        }

    def _find_instances(self) -> List[Match]:
        """Returns list of re.Match objects found on `self._text_no_crosswords`.

        Return:
            a list with all re.Match objects resulted from searching for
        """
        head = "TORNAR SEM EFEITO"
        end = " CAFEBABE"   # so that lookeahead does not become a problem
        # lis = self._processed_text.split(head)
        lis = self._text.split(head)
        lis = [
            re.search(self._inst_rule, head + tex + end)
            # content before first `head` occurrence does not matter
            for tex in lis[1:]
        ]
        lis = [i for i in lis if i]

        true_positive = []
        for raw_match in lis:
            flag = True
            for bad in self._BAD_MATCH_WORDS:
                grouped_match = raw_match.group()
                if len(grouped_match) > self._max_length or bad in grouped_match:
                    flag = False
                    break
            if flag:
                true_positive.append(raw_match)

        self._raw_matches = true_positive
        if self._debug:
            print("DEBUG:", len(lis), 'generic matches')
            print("DEBUG:", len(self._raw_matches), 'true matches')
        return [i.group() for i in self._raw_matches]

    # pylint: disable=too-many-locals,too-many-statements
    def _get_special_acts(self, lis_dict):
        for i, match in enumerate(self._raw_matches):
            act = match.group()
            curr_dict = lis_dict[i]
            data_dodf = curr_dict['data_dodf']
            if data_dodf == 'nan' or not data_dodf:
                data_dodf = re.search(
                    FLEX_DATE, self._raw_acts[i]
                )
                curr_dict['data_dodf'] = data_dodf

            numero_dodf = data_dodf and re.search(DODF_NUM, data_dodf.group())
            data_documento = data_dodf and \
                re.search(
                    FLEX_DATE, act[:data_dodf.start()] + act[data_dodf.end():])
            pagina_dodf = data_dodf and re.search(
                PAGE, act[data_dodf.end():][:50])

            nome = re.search(SERVIDOR_NOME_COMPLETO, act)
            if self._debug:
                print('NOME ENCONTRADO:', nome)
            if not nome:
                #  If it fails then a more generic regex is searched for
                dodf_mt = re.search(DODF, act)
                dodf_end = 0 if not dodf_mt else dodf_mt.end()
                nome = re.search(NOME_COMPLETO, act[dodf_end:])
                if self._debug:
                    print("NOME ENCONTRADO 2:", nome)
                del dodf_mt, dodf_end
                if not nome and self._nlp:
                    # Appeal to spacy
                    all_cands = re.findall(NOME_COMPLETO, act)
                    cand_text = 'SEM-SERVIDOR'
                    cand = None

                    for cand in self._nlp(', '.join([c.strip().title() for c in all_cands])).ents:
                        cand_text = cand.text

                        if cand.label_ == 'PER':
                            break

                    nome = re.search(cand_text.upper(), act)
                    del all_cands, cand_text, cand

            end_employee = nome.end() if nome else 0
            matricula = re.search(MATRICULA, act[end_employee:]) or \
                re.search(MATRICULA_GENERICO, act[end_employee:]) or \
                re.search(MATRICULA_ENTRE_VIRGULAS, act[end_employee:])

            del end_employee
            if not matricula or not nome:
                cargo_efetivo = None
            else:
                nome_start = act[nome.start():].find(
                    nome.group()) + nome.start()
                matricula_start = act[matricula.start():].find(
                    matricula.group()) + matricula.start()

                # NOTE: -1 is important in case `matricula` end with `,`
                if 0 <= (matricula_start - (nome_start + len(nome.group()))) <= 5:
                    # cargo_efetivo does not fit between 'nome' and 'matricula'
                    cargo_efetivo = re.search(
                        r",(?P<cargo_efetivo>[^,]+)", act[matricula_start + len(matricula.group())-1:])

                else:
                    # cargo_efetivo right after employee's name

                    cargo_efetivo = re.search(
                        r",(?P<cargo_efetivo>[^,]+)", act[nome_start + len(nome.group())-1:])
                del matricula_start, nome_start
            edicao = re.search(DODF_TIPO_EDICAO, act)
            tipo_edicao = re.search(TIPO_EDICAO, act[edicao.start()-1:edicao.end()+1])\
                if edicao else re.search("normal", "normal")
            curr_dict['data_documento'] = data_documento
            curr_dict['numero_dodf'] = numero_dodf
            curr_dict['pagina_dodf'] = pagina_dodf
            curr_dict['nome'] = nome
            curr_dict['matricula'] = matricula
            curr_dict['cargo_efetivo'] = cargo_efetivo
            curr_dict['tipo_edicao'] = tipo_edicao

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
        return (match,)

    @classmethod
    def _group_solver(cls, match):
        """Returns named group, or the whole match if no named groups
                are present on the match.
        Args:
            match: a re.Match object
        Returns: content of the unique named group found at match,
            the whole match if there are no groups at all or raise
            an exception if there are more than two groups.
        """
        if not match or isinstance(match, str):
            return np.nan

        if match.groupdict():
            key = list(match.groupdict())[0]
            return match.group(key)

        return match.group()

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
        _ = re.search(self._name, self._name)
        for dic in self._acts:
            dic["tipo_ato"] = _
        data = [{k: ( self._group_solver(v)
                      if k not in self._standard_props_names(capitalize=True)
                      else v ) for k, v in act.items()}
                for act in self._acts]

        return pd.DataFrame(data)
