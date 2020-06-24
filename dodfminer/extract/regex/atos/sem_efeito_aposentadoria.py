import pandas as pd
import re
# import spacy

# nlp=spacy.load('pt_core_news_sm')

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


DODF = r"(DODF|[Dd]i.rio\s+[Oo]ficial\s+[Dd]o\s+[Dd]istrito\s+[Ff]ederal)"

MONTHS_LOWER = (
    r'(janeiro|fevereiro|mar.o|abril|maio|junho|' \
    r'julho|agosto|setembro|outubro|novembro|dezembro)'
)

FLEX_DATE = r"(?P<date>\d+\s+(?:de\s*)?{}\s*(?:de\s*)?\d+|\d+[.]\d+[.]\d+|\d+[/]\d+[/]\d+)".format(case_insensitive(MONTHS_LOWER))

DODF_NUM = r"(DODF|[Dd]i.rio [Oo]ficial [Dd]o [Dd]istrito [Ff]ederal)\s*(n?r?o?[^\d]?)(?P<num>\d+)"
DODF_DATE = r"{}[^\n\n]{{0,50}}?(de\s?)?{}".format(DODF, FLEX_DATE)

SIAPE = r"{}\s*(?:n?.?)\s*[-\d.Xx/\s]".format(case_insensitive("siape"))

MATRICULA = r"(?:matr.cul.|matr?[.]?\B)[^\d]+(?P<matricula>[-\d.XxZzYz/\s]+)"

MATRICULA_GENERICO = r"(?<![^\s])(?P<matricula>([-\d.XxZzYz/\s]{1,})[.-][\dXxYy][^\d])"

MATRICULA_ENTRE_VIRGULAS = r"(?<=[A-Z]{3})\s*,\s+([-\d.XxZzYz/\s]{3,}?),"

# WARNING: "page_nums" may match not only nums.
# TODO: deal with edge cases like "p 33". There are only a few ones.
PAGE = r"((?:p\.|p.ginas?|p.?gs?\.?\b)(?P<page_nums>.{0,}?)(?=[,;:]|\n|\s[A-Z]|$))"

SERVIDOR_NOME_COMPLETO = r"servidora?\b.{0,40}?(?P<name>[A-ZÀ-Ž][.'A-ZÀ-Ž\s]{7,})"

NOME_COMPLETO = r"(?P<name>[.'A-ZÀ-Ž\s]{8,})"

EDICAO_DODF = r"(?P<edition>[Ss]uplement(o|ar)|[Ee]xtra|.ntegra)"

LOWER_LETTER = r"[áàâäéèẽëíìîïóòôöúùûüça-z]"
UPPER_LETTER = r"[ÁÀÂÄÉÈẼËÍÌÎÏÓÒÔÖÚÙÛÜÇA-Z]"

PROCESSO = r"(?P<processo>[-0-9/.]+)"

TIPO_DOCUMENTO = r"(portaria|ordem de servi.o|instrucao)"

class SemEfeitoAposentadoria:
    _name = "Atos Tornados sem Efeito (aposentadoria)"

    _raw_pattern = (
        r"TORNAR SEM EFEITO" + \
        r"([^\n]+\n){0,10}?[^\n]*?(tempo\sde\sservi.o|aposentadoria|aposentou|([Dd][Ee][Ss])?[Aa][Vv][Ee][Rr][Bb][Aa]..[Oo]|(des)?averb(ar?|ou))[\d\D]{0,500}?[.]\s" \
        r"(?=[A-Z]{4})"
    )

    _BAD_MATCH_WORDS = [
        "AVERBAR",
        "NOMEAR",
        # "CONCEDER ABONO DE PERMANENCIA",
        "CONCEDER",
        "EXONERAR",
        "DESAVERBAR",
        "APOSTILAR",
        "RETIFICAR",
    ]

    def __init__(self,file_name, text=False, nlp=None, debug=False):
        self._debug = debug
        self.nlp = nlp
        if not text:
            fp = open(file_name, "r")
            self._file_name = file_name
            self._text = fp.read()
            fp.close()
        else:
            self._file_name = ''
            self._text = file_name
        
        self._raw_matches = self._extract_raw_matches()
        self._processed_text = self._post_process_raw()
        self._final_matches = self._run_property_extraction()
        
        self._data_frame = self._build_dataframe()
    @classmethod
    def _self_match(cls, s:str, group_name: str):
        return re.match(fr'(?P<{group_name}>{s})', s)


    @property
    def data_frame(self):
        return self._data_frame

    @property
    def name(self):
        return self._name

    @property
    def acts_str(self):
        return self._processed_text    

    @property
    def props(self):
        return self._final_matches
    def _extract_raw_matches(self):
        """Returns list of re.Match objects found on `self._text`.

        Return:
            a list with all re.Match objects resulted from searching for
        """
        l = list(re.finditer(self._raw_pattern, self._text))
        if self._debug:
            print("DEBUG:", len(l), 'matches')
        return l


    def _post_process_raw(self):
        l = []
        for raw in self._raw_matches:
            s = raw.group()
            # Make sure words splitted accross lines are joined together
            no_split_word = s.replace('-\n', '-')
            
            # Makes easier to deal with the text.
            single_spaces = re.sub(r'\s+', r' ', no_split_word)
            
            # Sometimes more than one "TORNAR SEM EFEITO" is captured. Only the last
            # one hould matter.
            last_tornar_sem_efeito = single_spaces[single_spaces.rfind("TORNAR SEM EFEITO"):]
            l.append(last_tornar_sem_efeito)
        return l


    def _run_property_extraction(self):
        """Effectively extracts que information it was supposed to extract.
        For more details check "TCDF_requisitos" for KnEDLe project.

        Note:
            WARNING: this function tends to be very extense.
                Maybe a pipepilne-like approach would be better
                but haven't figured how to do so (yet).
        """
        # DODF date usually is easily extracted.
        tipo_lis = []
        processo_lis = []
        dodf_dates = []
        dodf_num = []
        tornado_sem_dates = []
        pages = []
        servidor_nome = []
        servidor_matricula = []
        cargo_efetivo_lis = []
        edicoes = []
        for tex in self._processed_text:
            tipo = re.search(TIPO_DOCUMENTO, tex[len("TORNAR SEM EFEITO"):], re.IGNORECASE)
            tipo_lis.append(tipo)
            processo = re.search(
                r"{}:?[^\d]{}(?P<processo>\d[-0-9./\s]*\d(?!\d))".format(case_insensitive("processo"), "{0,50}?",PROCESSO),
                tex)
            processo_lis.append(processo)

            
            # First, get DODF date.
            date_mt = re.search(DODF_DATE, tex)
            dodf_dates.append(date_mt)
            if date_mt:
                # seach for DODF num
                num = re.search(DODF_NUM, date_mt.group())
                if num:
                    if self._debug:
                        print('num.span():', num.span())
                    # num = re.search(fr'(?P<num>{date_mt.group()})', date_mt.group())
                dodf_num.append(num)

                # THEN lets search for publication date (heuristic)
                span = date_mt.span()
                removed_dodf_date = '{}{}'.format(tex[:span[0]], tex[span[1]:])
                published_date = re.search(FLEX_DATE, removed_dodf_date)
                tornado_sem_dates.append(published_date)
                # ALSO, page numbers (if present) come right after DODF date
                window = tex[span[1]:][:50]
                page = re.search(PAGE, window)                
                pages.append(page)

            else:
                tornado_sem_dates.append(None)
                dodf_num.append(None)
                pages.append(None)
            # Try to match employee
            servidor = re.search(SERVIDOR_NOME_COMPLETO, tex)
            if self._debug:
                print("SERVIDOR:", servidor)
            if not servidor:
                if self._debug:
                    print("SEM SERVIDOR!!!")
                #  If it fails then a more generic regex is searched for
                dodf_span = re.search(DODF, tex).span()
                # therefore `servidor` is not trustable when comes to start/end
                servidor = re.search(NOME_COMPLETO, tex[dodf_span[1]:])
                if not servidor:
                    # Appeal to spacy
                    all_cands = re.findall(
                        r"{}".format(NOME_COMPLETO),
                        tex
                    )
                    print("ALL_CANDS:", all_cands)
                    # print('\t(', *all_cands, sep=')\n\t(', end=')\n\n')
                    person_cands = []
                    for cand in self.nlp(', '.join([c.strip().title() for c in all_cands])).ents:
                        if cand.label_ == 'PER':
                            print(cand, 'IS THE PERSON')
                            break
                    servidor =  re.search(cand.text.upper(), tex)
            servidor_nome.append(servidor)
            
            if servidor:
                matricula = re.search(MATRICULA, tex[servidor.end():])
                if not matricula:
                    matricula = re.search(MATRICULA_GENERICO, tex[servidor.end():])
                    if not matricula:
                        matricula = re.search(MATRICULA_ENTRE_VIRGULAS, tex[servidor.end():] )
            else:
                matricula = None

            if not matricula or not servidor:
                cargo = None
            else:
                # TODO: improve robustness: cargo_efetivo is assumed to be either right after 
                # employee name or its matricula
                servidor = re.search(servidor.group(), tex)
                matricula = re.search(matricula.group(), tex)
                print("matricula.start() - servidor.end():", matricula.start() - servidor.end())
                # NOTE: -1 is important in case `matricula` end with `,`
                if 0 <= (matricula.start() - servidor.end()) <= 5:
                    # cargo NAO CABE entre 'servidor' e 'matricula'
                    print("CARGO DEPOIS DE MAATRICULA")
                    cargo = re.search(r",(?P<cargo>[^,]+)", tex[ matricula.end()-1: ])        
                else:
                    # cargo apohs nome do servidor
                    print("CARGO ANTES DE MATRICULA")
                    cargo = re.search(r",(?P<cargo>[^,]+)", tex[servidor.end()-1:])
            print("MATRICULA FINAL:", matricula.group())
            servidor_matricula.append(matricula)

            cargo_efetivo_lis.append(cargo)
            _ = DODF + r".{0,50}?" + EDICAO_DODF
            edicao = re.search(_, tex)

            if edicao:
                if re.search(r"\bextra\b", tex, re.IGNORECASE):
                    edicoes.append(re.search(r"\bextra\b", tex))
                elif re.search("\bsuplement(ar|o)\b", tex, re.IGNORECASE):
                    edicoes.append( re.search("\bsuplement(ar|o)\b", tex) )
                else:
                    edicoes.append( self._self_match("tipo-estranho", "edition") )
            else:
                edicoes.append(self._self_match("normal", "edition"))
        if self._debug:
            print(
                "tipo_lis:", len(tipo_lis), '\n',
                "processo_lis:", len(processo_lis), '\n',
                "dodf_dates:", len(dodf_dates), '\n',
                "dodf_num:", len(dodf_num), '\n',
                "tornado_sem_dates:", len(tornado_sem_dates), '\n',
                "pages:", len(pages), '\n',
                "servidor_nome:", len(servidor_nome), '\n',
                "servidor_matricula:", len(servidor_matricula), '\n',
                "cargo_efetivo:", len(cargo_efetivo_lis), '\n',
                "edicoes:", len(edicoes), '\n'

            )
        l = list(zip(
            tipo_lis,
            processo_lis,
            dodf_dates,
            dodf_num,
            tornado_sem_dates,
            pages,
            servidor_nome,
            servidor_matricula,
            cargo_efetivo_lis,
            edicoes
        ))
        if len(l) != len(self._processed_text):
            raise Exception("Processed matches and list of attributes differ! {} vs {}".format(
                len(self._processed_text), len(l)
            ))
        return l


    def _build_dataframe(self):
        def by_group_name(match):
            if match:
                keys = list(match.groupdict().keys())
                if len(keys) == 0:
                    return match.group()
                elif len(keys) > 1:
                    raise ValueError("Named regex must have AT MOST ONE NAMED GROUP.")
                if self._debug:
                    print('key: ', keys[0])
                return match.group(keys[0])
            else:
                return "nan"
        return pd.DataFrame(
            data=map(lambda lis: [by_group_name(i) for i in lis],self._final_matches),
            columns=[
                'tipo',
                'processo',
                'dodf_data',
                'dodf_num',
                'tse_data',
                'pag',
                'nome',
                'matricula',
                'cargo_efetivo',
                'tipo_edicao'
            ]
        )
    

