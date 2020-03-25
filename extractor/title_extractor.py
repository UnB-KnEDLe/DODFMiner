"""."""

import re
import json
from functools import reduce
from typing import List
from collections import namedtuple
import operator

import fitz
import title_filter

Box = namedtuple("Box", 'x0 y0 x1 y1')
TitlesSubtitles = namedtuple("TitlesSubtitles", "titles subtitles")
AuxT = namedtuple("Aux", "text type bbox page")
DODF_WIDTH = 765
DODF_HEIGHT = 907

TRASH_WORDS = [
    "SUMÁRIO",
    "DIÁRIO OFICIAL",
    "SEÇÃO (I|II|III)",
]

TRASH_COMPILED = re.compile('|'.join(TRASH_WORDS))

TYPE_TITLE, TYPE_SUBTITLE = "title", "subtitle"

def invert_auxt(aux: AuxT):
    """Reverse the type between TYPE_TITLE and TYPE_SUBTITLE.
    
    Args:
        aux: an instance of AuxT
    
    Returns:
        an copy of aux with its type field reversed
    """
    a1, _, a2, a3 = aux 
    return AuxT(a1, TYPE_TITLE if _ is TYPE_SUBTITLE else TYPE_SUBTITLE , a2, a3) 


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
                cond1 = flags in title_filter.BoldUpperCase.BOLD_FLAGS
                if cond1 and txt == txt.upper():
                    span['bbox'] = Box(*span['bbox'])
                    span['page'] = page.number
                    del span['color']
                    del span['flags']
                    lis.append(span)
    return lis


def extract_bold_pdf(path):
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


def get_titles_subtitles(lis):
    """Extract titles and subtitles from a list.

    Args:
        lis: a list of dict all of them having the keys:
            size -> float
            text -> str
            bbox -> Height
            page -> int
    Returns:
        TitlesSubtitles(titles=titles, subtitles=subtitles),
        where `titles` and `subtitles` are List[AuxT].
        Based on font size and heuristic.
    """
    # Sort by font size; take from biggest to smallest
    lis = sorted(lis, key=lambda d: d['size'], reverse=True)

    # Usually part of "Diário Oficial do DISTRITO FEDERAL"
    if "DISTRITO FEDERAL" in lis[0]['text']:
        del lis[0]
    # heuristic part: which font is the one use by titles?
    SZ = lis[min(2, len(lis) - 1)]['size']
    titles = []
    prev_el = lis[0]
    
    while lis:
        v = lis[0]        
    # for idx, v in enumerate(lis):
        if SZ == v['size']:
            if titles:
                cond1 = abs(prev_el['bbox'].y1 - v['bbox'].y0) < 10
                cond2 = prev_el['page'] == v['page']
                if cond1 and cond2:
                    titles[-1][0] = titles[-1][0] + "\n" + v['text']
                else:
                    titles.append([v['text'], TYPE_TITLE,
                                    v['bbox'], v['page']])
            else:
                titles.append([v['text'], TYPE_TITLE, v['bbox'], v['page']])
            lis = lis[1:]
        else:
            break
        prev_el = v
    titles = [AuxT(*i) for i in titles]
    sub_titles = []
    # if the list is over, there are no subtitles
    # if idx < len(lis):
    if lis:
        size = lis[0]['size']
        # PS: majority of subtitles uses only 1 line. Hard to distinguish
        # for _, v in enumerate(lis[idx:]):
        while lis:
            v = lis[0]
            # TODO deal with cases like "DEPARTAMENTO DE ESTRADAS DE
            # RODAGEM DO DISTRITO FEDERAL" (5/1/2005)
            if size == v['size']:
                sub_titles.append((v['text'], TYPE_SUBTITLE,
                                    v['bbox'], v['page']))
            else:   # this and next elements has others font sizes
                break
            lis = lis[1:]
        sub_titles = [AuxT(*i) for i in sub_titles]
    if not titles and sub_titles:
        return TitlesSubtitles( [invert_auxt(i) for i in sub_titles], titles )
    return TitlesSubtitles(titles, sub_titles)


def get_titles_subtitles_smart(path):
    """Extract titles and subtitles, making use of heuristics.

    Wrapper for _get_titles_subtitles, removing most of impurity
    (spans not which aren't titles/subtutles).
    """
    negrito_spans = reduce(operator.add, extract_bold_pdf(path))
    filtered1 = filter(title_filter.BoldUpperCase.dict_text,
                        negrito_spans)
    filtered2 = filter(lambda s: not re.search(TRASH_COMPILED,
                                                s['text']), filtered1)
    # 'calibri' as font apears as an noise
    filtered3 = filter(lambda x: 'calibri' not in x['font'].lower(), filtered2)
    ordered1 = sorted(filtered3,
                      key=lambda x: (-x['page'], x['size']),
                      reverse=True)
    return get_titles_subtitles(ordered1)
    

def extract(path: str) -> List[AuxT]:
    """Extract titles and subtitles from DODF pdf.
    Args:
        path: str indicating the path for the pdf to have its
            content extracted
    Returns:
        List[AuxT] containing all titles ans subtitles
    """
    titles_subtitles = get_titles_subtitles_smart(path)
    by_page = sort_2column(reduce(operator.add, titles_subtitles))
    return reduce(operator.add, by_page.values())


class ExtractorTitleSubtitle(object):
    """Use this class like that:
    >> path = "path_to_pdf"
    >> extractor = ExtractorTitleSubtitle(path)
    >> # To extract titles
    >> titles = extractor.titles
    >> # To extract subtitles
    >> titles = extractor.subtitles
    >> # To dump titles and subtitles on a json file
    >> json_path = "valid_file_name"
    >> extractor.dump_json(json_path)
    ."""


    def _mount_json(self):
        i = 0
        dic = {}
        aux = self._titles_subtitles
        while i < len(aux):
            el = aux[i]
            if el.type == TYPE_TITLE:
                title = el.text
                dic[title] = dic.get(title, [])
                i += 1
                while i < len(aux):
                    el = aux[i]
                    if el.type == TYPE_SUBTITLE:
                        dic[title].append(el.text)
                        i += 1
                    else:
                        break
            else:
                raise ValueError("Does not begin with a title")
        self._json = dic
        return self._json


    def _do_cache(self):
        self._titles_subtitles = extract(self._path)
        self._titles = list(filter(lambda x: x.type == TYPE_TITLE,
                                   self._titles_subtitles))
        self._subtitles = list(filter(lambda x: x.type == TYPE_SUBTITLE,
                                      self._titles_subtitles))
        self._mount_json()
        self._cached = True


    def __init__(self, path):
        """.

        Args:
            path: str indicating the path for the pdf to have its
                content extracted
        """
        self._titles_subtitles = TitlesSubtitles([], [])
        self._titles = []
        self._subtitles = []
        self._path = path
        self._cached = False
        self._json = dict()

    @property
    def titles(self):
        """All titles extracted from the file speficied by self._path."""
        if not self._cached:
            self._do_cache()
        return self._titles


    @property
    def subtitles(self):
        """All subtitles extracted from the file speficied by self._path."""
        if not self._cached:
            self._do_cache()
        return self._subtitles


    @property
    def json(self):
        """All titles and subtitles extracted from the file specified by
        self._path, hierarchically organized.
        
        BUG: as the titles repeats over the document's sections, only
            the subtitles related to the LAST appear os  a title  will remain.
        """
        if not self._json:
            if not self._cached:
                self._do_cache()
            self._mount_json()
        return self._json


    # TODO: add property which ensures title/subtitle hierarchy are kept
    

    def extract_all(self):
        """Extract all titles and subtitles on the path passed while
        instantiating that object. This function is not exepected to be
        needed.

        Ignores the cache.

        Returns:
            A list with titles and subtitles, sorted according to its
            reading order.
        """
        return self._extract()


    def dump_json(self, path):
        """Write on file specified by path the JSON representation of titles
        and subtitles extracted.

        Args:
            path: string containing path to .json file where the dump will
            be done. Its suffixed with ".json" if it's not.
        Returns:
            None.

        Dumps the titles and subtitles according to the hierarchy verified
        on the document.

        The outputfile should be specified and will be suffixed with the
        ".json" if it's not.
        """
        json.dump(self.json,
                  open(path + ((not path.endswith(".json")) * ".json"), 'w'),
                  ensure_ascii=False, indent='  ')

