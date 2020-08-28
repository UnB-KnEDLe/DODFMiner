import re
from typing import List, Match
import pandas as pd
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

DODF_DATE = DODF + r"[^\n\n]{0,50}?(de\s?)?" + FLEX_DATE

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


class SemEfeitoAposentadoria(Atos):
    _special_acts = [
        'numero_dodf', 'tornado_sem_efeito_publicacao',
        'pagina_dodf', 'nome', 'matricula',
        'cargo_efetivo', 'tipo_edicao',
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

    def _pre_process_text(self, s):
        # Make sure words splitted accross lines are joined together
        no_split_word = s.replace('-\n', '-')
        return no_split_word.replace('\n', ' ')

    def __init__(self, file, backend, debug=False, extra_search=True,
                 nlp=None, max_length=2000):
        self._max_length = max_length
        self._debug = debug
        self._extra_search = extra_search
        self._processed_text = self._pre_process_text(open(file).read())
        self._raw_matches = []
        self._nlp = nlp
        super().__init__(file, backend)

    def _act_name(self):
        return "Atos tornados sem efeito - aposentadoria"

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
            'tipo_documento ': TIPO_DOCUMENTO,
            'processo': PROCESSO_MATCH,
            'data_documento': DODF_DATE,
        }

    def _find_instances(self) -> List[Match]:
        """Returns list of re.Match objects found on `self._text_no_crosswords`.

        Return:
            a list with all re.Match objects resulted from searching for
        """
        head = "TORNAR SEM EFEITO"
        end = " CAFEBABE"   # so that lookeahead does not become a problem
        lis = self._processed_text.split(head)
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
                s = raw_match.group()
                if len(s) > self._max_length or bad in s:
                    flag = False
                    break
            if flag:
                true_positive.append(raw_match)

        self._raw_matches = true_positive
        if self._debug:
            print("DEBUG:", len(lis), 'generic matches')
            print("DEBUG:", len(self._raw_matches), 'true matches')
        return [i.group() for i in self._raw_matches]

    def _get_special_acts(self, lis_dict):
        for i, match in enumerate(self._raw_matches):
            act = match.group()
            curr_dict = lis_dict[i]
            dodf_date = curr_dict['data_dodf']
            dodf_num = dodf_date and re.search(DODF_NUM, dodf_date.group())
            tornado_sem_efeito_publicacao = dodf_date and \
                re.search(
                    FLEX_DATE, act[:dodf_date.start()] + act[dodf_date.end():])
            dodf_pagina = dodf_date and re.search(
                PAGE, act[dodf_date.end():][:50])

            servidor = re.search(SERVIDOR_NOME_COMPLETO, act)
            if not servidor:
                #  If it fails then a more generic regex is searched for
                dodf_mt = re.search(DODF, act)
                dodf_end = 0 if not dodf_mt else dodf_mt.end()
                servidor = re.search(NOME_COMPLETO, act[dodf_end:])
                del dodf_mt, dodf_end
                if not servidor:
                    # Appeal to spacy
                    all_cands = re.findall(NOME_COMPLETO, act)
                    cand_text = 'SEM-SERVIDOR'
                    for cand in self._nlp(', '.join([c.strip().title() for c in all_cands])).ents:
                        cand_text = cand.text

                        if cand.label_ == 'PER':
                            break
                    servidor = re.search(cand_text.upper(), act)
                    del all_cands, cand_text, cand
            end_employee = servidor.end() if servidor else 0
            matricula = re.search(MATRICULA, act[end_employee:]) or \
                re.search(MATRICULA_GENERICO, act[end_employee:]) or \
                re.search(MATRICULA_ENTRE_VIRGULAS, act[end_employee:])

            del end_employee
            if not matricula or not servidor:
                cargo = None
            else:
                servidor_start = act[servidor.start():].find(
                    servidor.group()) + servidor.start()
                matricula_start = act[matricula.start():].find(
                    matricula.group()) + matricula.start()

                # NOTE: -1 is important in case `matricula` end with `,`
                if 0 <= (matricula_start - (servidor_start + len(servidor.group()))) <= 5:
                    # cargo does not fit between 'servidor' and 'matricula'
                    cargo = re.search(
                        r",(?P<cargo>[^,]+)", act[matricula_start + len(matricula.group())-1:])

                else:
                    # cargo right after employee's name

                    cargo = re.search(
                        r",(?P<cargo>[^,]+)", act[servidor_start + len(servidor.group())-1:])
                del matricula_start, servidor_start
            edicao = re.search(DODF_TIPO_EDICAO, act)
            dodf_tipo_edicao = re.search(TIPO_EDICAO, act[edicao.start()-1:edicao.end()+1])\
                if edicao else re.search("normal", "normal")
            curr_dict['numero_dodf'] = dodf_num
            curr_dict['tornado_sem_efeito_publicacao'] = tornado_sem_efeito_publicacao
            curr_dict['pagina_dodf'] = dodf_pagina
            curr_dict['nome'] = servidor
            curr_dict['matricula'] = matricula
            curr_dict['cargo_efetivo'] = cargo

            curr_dict['tipo_edicao'] = dodf_tipo_edicao

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
        return match,

    def _group_solver(self, match):
        """Returns named group, or the whole match if no named groups
                are present on the match.
        Args:
            match: a re.Match object
        Returns: content of the unique named group found at match,
            the whole match if there are no groups at all or raise
            an exception if there are more than two groups.
        """
        if not match or isinstance(match, str):
            return "nan"
        elif match.groupdict():
            key = list(match.groupdict())[0]
            return match.group(key)
        else:
            return match.group()

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

    def _build_dataframe(self):
        _ = re.search(self._name, self._name)
        for dic in self._acts:
            dic["tipo_ato"] = _
        data = [{k: self._group_solver(v) for k, v in act.items()}
                for act in self._acts]
        return pd.DataFrame(data)
