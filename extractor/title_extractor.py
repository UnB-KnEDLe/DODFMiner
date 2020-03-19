"""Missing File Doc."""

import re
import json
from functools import reduce
from typing import List
from collections import namedtuple
import operator

import fitz
import extractor.title_filter as title_filter

Box = namedtuple("Box", ['x0', 'y0', 'x1', 'y1'])
AuxT = namedtuple("Aux", "text type bbox page")
DODF_WIDTH = 765
DODF_HEIGHT = 907


def load_blocks_list(path):
    """Loads list of blocks list from the file specified.
    Args:
        path: str with path to DODF pdf file
    Returns:
        A list with page blocks, each element being a list with its
        according page blocks
    """
    doc = fitz.open(path)
    return [p.getTextPage().extractDICT()['blocks'] for p in doc]


def extract_bold_upper_page(page: fitz.fitz.Page):
    """Extract page content which have bold font and are uppercase.
    Args:
        page: an fitz.fitz.Page object to have its bold content extracted
    Returns:
        A list containing all bold (and simultaneously upper)
        content at the page
    """
    lis = []
    for bl in page.getTextPage().extractDICT()['blocks']:
        for line in bl['lines']:
            for span in line['spans']:
                flags = span['flags']
                txt: str = span['text']
                if flags in (16, 20) and txt == txt.upper():
                    span['bbox'] = Box(*span['bbox'])
                    span['page'] = page.number
                    del span['color']
                    del span['flags']
                    lis.append(span)
    return lis


def extrai_bold_pdf(path):
    """Extract bold content from DODF pdf.
    Args:
        path: an path to a DODF pdf file
    Returns:
        a list of list of bold span text
    """
    doc = fitz.open(path)
    return [extract_bold_upper_page(page) for page in doc]


def group_by_page(lis):
    """Groups each of lis elements by its page number.

    Essentially a "groupby" where the key is the page number of each span.
    Returns a dict with spans of each page, being keys the page numbers.
    """
    numbers = dict()
    for page_num in set(map(lambda x: x.page, lis)):
        numbers[page_num] = []
    for el in lis:
        numbers[el.page].append(el)
    return numbers


def sort_by_column(lis, width=DODF_WIDTH):
    """Sorts lis elements asuming they are on the same page and on a 2-column layout.

    Args:
        lis: a list with AuxT elements
        width: the page width (the context in which all lis elements
            were originally)
    Returns:
        A list containing the lis elements sorted according to:
            1. columns
            2. position on column
        Assumes a 2-column page layout. All elements on the left column will
        be placed first of any element on the right one. Inside each columns,
        reading order is espected to be kept.
    """
    lr = [[], []]
    MID_W = width / 2
    for i in lis:
        if i.bbox.x0 < MID_W:
            lr[0].append(i)
        else:
            lr[1].append(i)
    ordenado = map(lambda x: sorted(x, key=lambda x: x.bbox.y0), lr)
    return reduce(operator.add, ordenado)


def sort_2column(lis):
    """Missing Summary.

    Sorts a list of AuxT objects, assuming a full 2-columns
    layout over whatever document lis are extracted from.
    """
    by_page = group_by_page(lis)
    ordered_by_page = {idx: sort_by_column(lis) for idx, lis in
                       sorted(by_page.items())}
    return ordered_by_page


TitulosSubtitulos = namedtuple("TitulosSubtitulos", "titulos subtitulos")
AuxT = namedtuple("Aux", "text type bbox page")


class ExtratorTituloSubTitulo(object):
    """Use this class like that:
    >> path = "path_to_pdf"
    >> extractor = ExtratorTituloSubTitulo(path)
    >> # To extract titulos
    >> titles = extractor.titulos
    >> # To extract subtitulos
    >> titles = extractor.subtitulos
    >> # To dump titulos and subtitulos on a json file
    >> json_path = "valid_file_name"
    >> extractor.dump_json(json_path)
    ."""

    TRASH_WORDS = [
        "SUMÁRIO",
        "DIÁRIO OFICIAL",
        "SEÇÃO (I|II|III)"
    ]

    TRASH_COMPILED = re.compile('|'.join(TRASH_WORDS))

    @staticmethod
    def _get_titulos_subtitulos(lis):
        """Missing Summary.

        Receber lista com dictionários com chaves:
        Expect 'lis' to be a list of dict all of them having the keys:
          - size -> float
          - text -> str
          - bbox -> Height
          - page -> int
        Returns TitulosSubtitulos(titulos=titulos, subtitulos=subtitulos),
        where `titulos` and `subtitulos` are List[AuxT]
        Base on font size and heuristic.
        """
        # Ordenar pelo tamanho da fonte, pegar da maior ateh a menor
        lis = sorted(lis, key=lambda d: d['size'], reverse=True)

        if "DISTRITO FEDERAL" in lis[0]['text']:
            del lis[0]
        SZ = lis[min(2, len(lis))]['size']
        titles = []
        prev_el = lis[0]
        for i, v in enumerate(lis):
            if SZ == v['size']:
                if titles:
                    cond1 = abs(prev_el['bbox'].y1 - v['bbox'].y0) < 10
                    cond2 = prev_el['page'] == v['page']
                    if cond1 and cond2:
                        titles[-1][0] = titles[-1][0] + " " + v['text']
                    else:
                        titles.append([v['text'], 'titulo',
                                       v['bbox'], v['page']])
                else:
                    titles.append([v['text'], 'titulo', v['bbox'], v['page']])
            else:
                break
            prev_el = v
        titles = [AuxT(*i) for i in titles]
        sub_titles = []
        size = lis[i]['size']
        # PS: maioria dos subtitulos ocupa 1 linha só;
        for _, v in enumerate(lis[i:]):
            # TODO tratar outros casos como "DEPARTAMENTO DE ESTRADAS DE
            # RODAGEM DO DISTRITO FEDERAL" (5/1/2005)
            if size == v['size']:
                sub_titles.append((v['text'], 'subtitulo',
                                   v['bbox'], v['page']))
            else:
                break
        sub_titles = [AuxT(*i) for i in sub_titles]
        return TitulosSubtitulos(titles, sub_titles)

    @staticmethod
    def _get_titulos_subtitulos_smart(path):
        """Extract titulos and subtitulos, making use of heuristics.

        Wrapper for _get_titulos_subtitulos, removing most of impurity
        (spans not which aren't titles/subtutles).
        """
        negrito_spans = reduce(operator.add, extrai_bold_pdf(path))
        filtrado1 = filter(title_filter.NegritoCaixaAlta.dict_text,
                           negrito_spans)
        filtrado2 = filter(lambda s: not re.search(ExtratorTituloSubTitulo.TRASH_COMPILED,
                                                   s['text']), filtrado1)
        ordenado1 = sorted(filtrado2,
                           key=lambda x: (-x['page'], x['size']),
                           reverse=True)
        return ExtratorTituloSubTitulo._get_titulos_subtitulos(ordenado1)

    def _mount_json(self):
        i = 0
        dic = {}
        aux = self._titulos_subtitulos
        while i < len(aux):
            el = aux[i]
            if el.type == 'titulo':
                titulo = el.text
                dic[titulo] = []
                i += 1
                while i < len(aux):
                    el = aux[i]
                    if el.type == 'subtitulo':
                        dic[titulo].append(el.text)
                        i += 1
                    else:
                        break
            else:
                raise ValueError("Não começa com títulos")
        self._json = dic
        return self._json

    def _extract(self):
        a = ExtratorTituloSubTitulo._get_titulos_subtitulos_smart(self._path)
        titulos_subtitulos = a
        by_page = sort_2column(reduce(operator.add, titulos_subtitulos))
        return reduce(operator.add, by_page.values())

    def _do_cache(self):
        self._titulos_subtitulos = self._extract()
        self._titulos = list(filter(lambda x: x.type == 'titulo',
                                    self._titulos_subtitulos))
        self._subtitulos = list(filter(lambda x: x.type == 'subtitulo',
                                       self._titulos_subtitulos))
        self._mount_json()
        self._cached = True

    def __init__(self, path):
        """Missing Doc."""
        self._negrito = load_blocks_list(path)
        self._titulos_subtitulos = TitulosSubtitulos([], [])
        self._titulos = []
        self._subtitulos = []
        self._path = path
        self._cached = False
        self._json = dict()

    @property
    def titulos(self):
        """All titulos extracted from the file speficied by self._path."""
        if not self._cached:
            self._do_cache()
        return self._titulos

    @property
    def subtitulos(self):
        """All subtitulos extracted from the file speficied by self._path."""
        if not self._cached:
            self._do_cache()
        return self._subtitulos

    @property
    def json(self):
        """All titulos and subtitulos extracted from the file specified by
        self._path, hierarchically organized."""
        if not self._json:
            if not self._cached:
                self._do_cache()
            self._mount_json()
        return self._json

    def extract_all(self):
        """Extract all titutos and subtitulos on the path passed while
        instantiating that object. This function is not exepected to be
        needed.

        Ignores the cache.

        Returns:
            A list with titulos and subtitulos, sorted according to its
            reading order.
        """
        return self._extract()

    def dump_json(self, path):
        """Write on file specified by path the JSON representation of titulos and
        subtitulos extracted.

        Args:
            path: string containing path to .json file where the dump will
            be done. Its suffixed with ".json" if it's not.
        Returns:
            None.

        Dumps the titulos and subtitulos according to the hierarchy verified
        on the document.

        The outputfile should be specified and will be suffixed with the
        ".json" if it's not.
        """
        json.dump(self.json,
                  open(path + ((not path.endswith(".json")) * ".json"), 'w'),
                  ensure_ascii=False, indent='  ')
