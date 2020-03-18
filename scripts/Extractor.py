import re
import json
from functools import reduce
from typing import List
from collections import namedtuple
import operator

import fitz
import Filter

Box = namedtuple("Box", ['x0', 'y0', 'x1', 'y1'])
AuxT = namedtuple("Aux","text type bbox page")

def load_blocks_list(path):
    """Returns list with page blocks, where each element is a list with its according page blocks
    da pahgina correspondente."""
    doc = fitz.open(path)
    return [ p.getTextPage().extractDICT()['blocks']    for p in doc]

def extrai_negrito_pagina(page: fitz.fitz.Page) -> List[dict]:
    """
    Returns span list containing all bold (and simultaneously upper) content of a page.
    """
    lis = []
    for bl in page.getTextPage().extractDICT()['blocks']:
        for line in bl['lines']:
            for span in line['spans']:
                ft = span['font']
                flags = span['flags']
                txt: str = span['text']
                if flags in (16, 20) and txt == txt.upper():
                    # Nao apagar as alturas para depois remontar os títulos quebrados
                    span['bbox'] = Box(*span['bbox'])
                    span['page'] = page.number    # importante para nao concatenar errado títulos
                    del span['color']
                    del span['flags']
                    lis.append(span)
    return lis

def extrai_negrito_pdf(path: str) -> List[List[dict]]:
    """
    Receives file's path.
    Returns list of list of bold span text.
    """
    doc = fitz.open(path)
    return [extrai_negrito_pagina(page) for page in doc]

def group_by_page(lis: List[AuxT]) -> dict:
    """
    Essentially a "groupby" where the key is the page number of each span.
    Returns a dict with spans of each page, being keys the page numbers.
    """
    numbers = dict()
    for page_num in set(map(lambda x: x.page, lis)):
            numbers[ page_num ] = []
    for el in lis:
            numbers[el.page].append( el )
    return numbers

def sort_by_column(lis: List[AuxT], width=765, height=907):
    """
    Assumes lis contains spans on the SAME PAGE and sorts it based:
        1. columns
        2. position on column
    Assumes a 2-column page layout.
    """
    lr = [[], []]
    MID_W = width / 2
    for i in lis:
        if i.bbox.x0 < MID_W: lr[0].append(i)
        else: lr[1].append(i)
    ordenado = map( lambda x: sorted(x, key=lambda x: x.bbox.y0), lr )
    return reduce( operator.add, ordenado )

def sort_2column(lis: List[AuxT], width=765, height=907) -> dict:
    """
    Sorts a list of AuxT objects, assuming a full 2-columns layout over whatever document
    lis are extracted from.
    """
    by_page = group_by_page(lis)
    ordered_by_page = {idx: sort_by_column(lis) for idx, lis in sorted(by_page.items()) }
    return ordered_by_page


TitulosSubtitulos = namedtuple("TitulosSubtitulos", "titulos subtitulos")
AuxT = namedtuple("Aux","text type bbox page")

class ExtratorTituloSubTitulo(object):

    TRASH_WORDS = [
        "SUMÁRIO",
        "DIÁRIO OFICIAL",
        "SEÇÃO (I|II|III)"
    ]

    TRASH_COMPILED = re.compile('|'.join(TRASH_WORDS))
    @staticmethod
    def _get_titulos_subtitulos(lis: List[dict]) -> TitulosSubtitulos:
        """
        Receber lista com dictionários com chaves:
        Expect 'lis' to be a list of dict all of them having the keys:
            - size -> float
            - text -> str
            - bbox -> Height
            - page -> int
        Returns TitulosSubtitulos(titulos=titulos, subtitulos=subtitulos), where
        `titulos` and `subtitulos` are List[AuxT]
        Base on font size and heuristic.
        """
        # Ordenar pelo tamanho da fonte, pegar da maior ateh a menor
        lis = sorted(lis, key=lambda d:d['size'], reverse=True)

        if "DISTRITO FEDERAL" in lis[0]['text']:
            del lis[0]
        SZ = lis[ min(2, len(lis)) ]['size']
        titles = []
        prev_el = lis[0]
        for i, v in enumerate( lis ):
            if SZ == v['size']:
                if titles:
                    if abs(prev_el['bbox'].y1 - v['bbox'].y0) < 10 and prev_el['page'] == v['page']:
                        titles[-1][0] = titles[-1][0] + " " + v['text']
                    else:
                        titles.append( [v['text'], 'titulo', v['bbox'], v['page']] )
                else:
                    titles.append([v['text'], 'titulo', v['bbox'], v['page']])
            else:
                break
            prev_el = v
        titles = [AuxT(*i) for i in titles]
        sub_titles = []
        size = lis[i]['size']
        for _, v in enumerate(lis[i:]): # PS: maioria dos subtitulos ocupa 1 linha só;
            # TODO tratar outros casos como "DEPARTAMENTO DE ESTRADAS DE RODAGEM DO DISTRITO FEDERAL" (5/1/2005)
            if size == v['size']:
                sub_titles.append((v['text'], 'subtitulo', v['bbox'], v['page']))
            else:
                break
        sub_titles = [AuxT(*i) for i in sub_titles]
        return TitulosSubtitulos(titles, sub_titles)

    @staticmethod
    def _get_titulos_subtitulos_smart(path):
        """
        Wrapper for _get_titulos_subtitulos, removing most of impurity
        (spans not which aren't titles/subtutles).
        """
        negrito_spans = reduce(operator.add, extrai_negrito_pdf(path))
        filtrado1 = filter(Filter.NegritoCaixaAlta.dict_text, negrito_spans)
        filtrado2 = filter( lambda s: not re.search(ExtratorTituloSubTitulo.TRASH_COMPILED, s['text']),    filtrado1)
        ordenado1 = sorted(filtrado2, key=lambda x: (-x['page'], x['size']), reverse=True)
        return ExtratorTituloSubTitulo._get_titulos_subtitulos(ordenado1)


    def _mount_json(self) -> dict:
        i = 0
        dic = {}
        aux = self._titulos_subtitulos
        while i < len(aux):
            el = aux[i]
            if el.type == 'titulo':
                titulo = el.text
                dic[ titulo ] = []
                i += 1
                while i < len(aux):
                    el = aux[i]
                    if el.type == 'subtitulo':
                        dic[ titulo ].append(el.text)
                        i += 1
                    else:
                        break
            else:
                raise ValueError("Não começa com títulos")
        self._json = dic
        return self._json

    def _extract(self) -> List[AuxT]:
        titulos_subtitulos = ExtratorTituloSubTitulo._get_titulos_subtitulos_smart( self._path )
        by_page = sort_2column( reduce(operator.add, titulos_subtitulos) )
        return reduce(operator.add, by_page.values() )

    def _do_cache(self) -> None:
        self._titulos_subtitulos = self._extract()
        self._titulos = list(filter(lambda x: x.type == 'titulo', self._titulos_subtitulos))
        self._subtitulos = list(filter(lambda x: x.type == 'subtitulo', self._titulos_subtitulos))
        self._mount_json()
        self._cached = True

    def __init__(self, path):
        self._negrito = load_blocks_list(path)
        self._titulos_subtitulos = TitulosSubtitulos([], [])
        self._titulos = []
        self._subtitulos = []
        self._path = path
        self._cached = False
        self._json = dict()

    @property
    def titulos(self) -> List[AuxT]:
        if not self._cached:
            self._do_cache()
        return self._titulos

    @property
    def subtitulos(self) -> List[AuxT]:
        if not self._cached:
            self._do_cache()
        return self._subtitulos

    @property
    def json(self) -> dict:
        if not self._json:
            if not self._cached:
                self._do_cache()
            self._mount_json()
        return self._json

    def extract_all(self) -> List[AuxT]:
        """
        Retorna lista com títulos/subtítulos, ordenados segundo ordem de leitura.
        Ignora o cache.
        """
        return self._extract()

    def dump_json(self, path: str):
        """
        Dumps the titulos and subtitulos according to the hierarchy verified on the document.
        The outputfile should be specifiend and will be suffixed with the ".json" if its not.
        """
        json.dump(self.json, open(path + ((not path.endswith(".json")) * ".json"), 'w')
        , ensure_ascii=False, indent='    ')
