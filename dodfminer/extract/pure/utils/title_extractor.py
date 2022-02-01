"""
    Extract Title and Subtitles.
"""

# TODO: Improve docummentation
# TODO: Remove global variables and functions

from typing import List
from functools import reduce
from collections import namedtuple

import os
import re
import json
import operator
import fitz

from dodfminer.extract.pure.utils import title_filter

Box = namedtuple("Box", "x0 y0 x1 y1")
BBox = namedtuple("BBox", "bbox")
TitlesSubtitles = namedtuple("TitlesSubtitles", "titles subtitles")
TextTypeBboxPageTuple = namedtuple(
    "TextTypeBboxPageTuple", "text type bbox page")

_TRASH_WORDS = [
    "SUMÁRIO",
    "DIÁRIO OFICIAL",
    "SEÇÃO (I|II|III)",
]

_TRASH_COMPILED = re.compile('|'.join(_TRASH_WORDS))

_TYPE_TITLE, _TYPE_SUBTITLE = "title", "subtitle"
_TITLE_MULTILINE_THRESHOLD = 10


def load_blocks_list(path):
    """Loads list of blocks list from the file specified.

    Args:
        path: string with path to DODF pdf file

    Returns:
        A list with page blocks, each element being a list with its
        according page blocks.

    """
    doc = fitz.open(path)
    return [p.get_textpage().extractDICT()['blocks'] for p in doc]


def group_by_column(elements, width):
    """Groups elements by its culumns.
    The sorting assumes they are on the same page
    and on a 2-column layout.

    Essentially a "groupby" where the key is the page number of each span.

    Args:
        elements: Iterable[TextTypeBboxPageTuple] sorted by its page
                  number to be grouped.

    Returns:
        A dict with spans of each page, being keys the page numbers.

    """
    left_right = [[], []]
    mid_width = width / 2
    for i in elements:
        if i.bbox.x0 <= mid_width:
            left_right[0].append(i)
        else:
            left_right[1].append(i)
    return left_right


def group_by_page(elements):
    """Groups elements by page number.

    Essentially a "groupby" where the key is the page number of each span.

    Args:
        elements: Iterable[TextTypeBboxPageTuple] sorted by its page
                  number to be grouped.

    Returns:
        A dict with spans of each page, being keys the page numbers.

    """
    page_elements = {}
    for page_num in set(map(lambda x: x.page, elements)):
        page_elements[page_num] = []
    for element in elements:
        page_elements[element.page].append(element)
    return page_elements


def sort_by_column(elements, width):
    """Sorts list elements by columns.

    Args:
        elements: Iterable[TextTypeBboxPageTuple].
        width: the page width (the context in which all list elements
            were originally).

    Returns:
        List[TextTypeBboxPageTuple] containing the list elements
        sorted according to:
            1. columns
            2. position on column
        Assumes a 2-column page layout. All elements on the left column will
        be placed first of any element on the right one. Inside each columns,
        reading order is expected to be kept.

    """
    left_right = group_by_column(elements, width)

    # Sort by height
    ordenado = (sorted(i, key=lambda x: x.bbox.y0) for i in left_right)
    return reduce(operator.add, ordenado)


def invert_text_type_bbox_page_tuple(text_type_bbox_page_tuple):
    """Reverses the type between _TYPE_TITLE and _TYPE_SUBTITLE.

    Args:
        textTypeBboxPageTuple: instance of TextTypeBboxPageTuple.

    Returns:
        copy of textTypeBboxPageTuple with its type field reversed.

    """
    text, _type, bbox, page = text_type_bbox_page_tuple
    return TextTypeBboxPageTuple(text, _TYPE_TITLE if _type is _TYPE_SUBTITLE
                                 else _TYPE_SUBTITLE, bbox, page)


def _extract_bold_upper_page(page):
    """Extracts page content which have bold font and are uppercase.

    Args:
        page: fitz.fitz.Page object to have its bold content extracted.

    Returns:
        A list containing all bold (and simultaneously upper)
        content at the page.

    """
    lis = []
    for block in page.get_textpage().extractDICT()['blocks']:
        for line in block['lines']:
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


def _extract_bold_upper_pdf(doc):
    """Extracts bold content from DODF pdf.

    Args:
        doc: DODF pdf file returned by `fitz.open`

    Returns:
        a list of list of bold span text

    """
    return [_extract_bold_upper_page(page) for page in doc]


def sort_2column(elements, width_lis):
    """Sorts TextTypeBboxPageTuple iterable.

    Sorts sequence of TextTypeBboxPageTuple objects, assuming a full 2-columns
    layout over them.

    Args:
        elements: Iterable[TextTypeBboxPageTuple]
    Returns:
        dictionary mapping page number to its elements sorted by column
        (assumig there are always 2 columns per page)
    """
    by_page = group_by_page(elements)
    ordered_by_page = {idx: sort_by_column(elements, width=width_lis[idx]) for idx, elements in
                       sorted(by_page.items())}
    return ordered_by_page


# TODO: deal with `subtitles` using homogeneous reasoning
# (pretty much what was done on `titles`, so that the
# multiline are correctly assembled)
def _get_titles_subtitles(elements, width_lis):
    """Extracts titles and subtitles from list. WARNING: Based on font size and heuristic.

    Args:
        titles_subtitles: a list of dict all of them having the keys:
            size -> float
            text -> str
            bbox -> Box
            page -> int

    Returns:
        TitlesSubtitles[List[TextTypeBboxPageTuple], List[TextTypeBboxPageTuple]].

    """
    # mainly to remove "DISTRITO FEDERAL" trash below
    elements = sorted(
        elements, key=lambda d: d['size'], reverse=True)

    # Usually part of "Diário Oficial do DISTRITO FEDERAL"
    if "DISTRITO FEDERAL" in elements[0]['text']:
        del elements[0]

    # heuristic part: which font is the one use by titles?

    guessed_title_font_size = elements[min(
        2, len(elements) - 1)]['size']
    titles = []
    previous_element = elements[0]

    while elements:
        current_element = elements[0]
        if guessed_title_font_size == current_element['size']:
            if titles:
                cond1 = abs(
                    previous_element['bbox'].y1 - current_element['bbox'].y0) < _TITLE_MULTILINE_THRESHOLD
                cond2 = previous_element['page'] == current_element['page']

                # Titles must be also in the same column

                column_grouped = group_by_column((BBox(previous_element['bbox']), BBox(current_element['bbox'])),
                                                 width=width_lis[current_element['page']])
                cond3 = not (column_grouped[0] and column_grouped[1])
                if cond1 and cond2 and cond3:
                    titles[-1][0].append(current_element['text'])
                else:
                    titles.append([[current_element['text']], _TYPE_TITLE,
                                   current_element['bbox'],
                                   current_element['page']])
            else:
                titles.append([[current_element['text']], _TYPE_TITLE,
                               current_element['bbox'],
                               current_element['page']])
            elements = elements[1:]
            previous_element = current_element
            continue
        break

    # Titles with more than one line should be a single string

    titles = [TextTypeBboxPageTuple("\n".join(i[0]), *i[1:]) for i in titles]
    sub_titles = []
    # if the elements is over, there are no subtitles
    if elements:
        size = elements[0]['size']

        # PS: majority of subtitles uses only 1 line. Hard to distinguish
        while elements:
            current_element = elements[0]
            # TODO deal with cases like "DEPARTAMENTO DE ESTRADAS DE
            # RODAGEM DO DISTRITO FEDERAL" (5/1/2005)
            if size == current_element['size']:
                sub_titles.append((current_element['text'], _TYPE_SUBTITLE,
                                   current_element['bbox'],
                                   current_element['page']))
                elements = elements[1:]
                continue
            break
        sub_titles = [TextTypeBboxPageTuple(*i) for i in sub_titles]

    # Sometimes heuristic fails. However, the fix below seems to work on most
    # cases.
    # Happens mostly when there are only one title and other stuffs.

    if not titles and sub_titles:
        return TitlesSubtitles([invert_text_type_bbox_page_tuple(i) for i in sub_titles], titles)

    return TitlesSubtitles(titles, sub_titles)


def _get_titles_subtitles_smart(doc, width_lis):
    """Extracts titles and subtitles. Makes use of heuristics.

    Wraps _get_titles_subtitles, removing most of impurity
    (spans not which aren't titles/subtutles).

    Args:
        doc: DODF pdf file returned by `fitz.open`

    Returns:
        TitlesSubtitles(List[TextTypeBboxPageTuple],
                        List[TextTypeBboxPageTuple]).
    """
    bold_spans = reduce(operator.add, _extract_bold_upper_pdf(doc))
    filtered1 = filter(title_filter.BoldUpperCase.dict_text, bold_spans)
    filtered2 = filter(lambda s: not re.search(
        _TRASH_COMPILED, s['text']), filtered1)
    # 'calibri' as font apears sometimes, however never in titles or subtitles

    filtered3 = filter(lambda x: 'calibri' not in x['font'].lower(), filtered2)

    # TODO: check for necessity of this sorting
    ordered1 = sorted(filtered3,
                      key=lambda x: (-x['page'], x['size']),
                      reverse=True)
    return _get_titles_subtitles(ordered1, width_lis)


def extract_titles_subtitles(path):
    """Extracts titles and subtitles from DODF pdf.

    Args:
        path: str indicating the path for the pdf to have its
            content extracted.

    Returns:
        List[TextTypeBboxPageTuple] containing all titles ans subtitles.

    """
    doc = fitz.open(path)
    width_lis = [p.MediaBox[2] for p in doc]

    titles_subtitles = _get_titles_subtitles_smart(doc, width_lis=width_lis)
    by_page = sort_2column(
        reduce(operator.add, titles_subtitles), width_lis=width_lis)
    return reduce(operator.add, by_page.values())


# TODO: use tuples instead of lists for ensure
# immutability and avoid unexpected behavior
# (e.g, user modifying internal state of an ExtractorTitleSubtitle
# instance through appending elements to its internals lists)


class ExtractorTitleSubtitle:
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

    _TITLE_MULTILINE_THRESHOLD = 10

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
        self._json = {}
        self._hierarchy = []

    def _mount_json(self):
        """Mounts json containing titles with its associated subtitles
        and store it at self._json.

        Returns:
            self._json
        """
        i = 0
        _json = {}
        titles_subtitles = self._titles_subtitles
        limit = len(titles_subtitles)
        while i < limit:
            current_element = titles_subtitles[i]
            if current_element.type == _TYPE_TITLE:
                title = current_element.text
                _json[title] = _json.get(title, [])
                i += 1
                while i < limit:
                    current_element = titles_subtitles[i]
                    if current_element.type == _TYPE_SUBTITLE:
                        _json[title].append(current_element.text)
                        i += 1
                    else:
                        break
            else:
                print("Does not begin with a title")
                i += 1
        _json = {k: tuple(val) for k, val in _json.items()}
        self._json = _json
        return self._json

    def _mount_hierarchy(self):
        """Mounts list containing titles with its associated subtitles
        and store it at self._hierarchy.

        Returns:
            self._hierarchy
        """
        i = 0
        hierarchy = []
        titles_subtitles = self._titles_subtitles
        limit = len(titles_subtitles)
        while i < limit:
            current_element = titles_subtitles[i]
            if current_element.type == _TYPE_TITLE:
                title = current_element.text
                hierarchy.append([title, []])
                i += 1
                while i < limit:
                    current_element = titles_subtitles[i]
                    if current_element.type == _TYPE_SUBTITLE:
                        hierarchy[-1][1].append(current_element.text)
                        i += 1
                    else:
                        break
            else:
                raise ValueError("Não começa com títulos")
        self._hierarchy = [TitlesSubtitles(*i) for i in hierarchy]
        return self._hierarchy

    def _do_cache(self):
        """Computes some internal attributes.

        So that no more computations are needed for them.
        Implicit called after first access to some property.
        Computes and caches the following internal attributes:
            - _titles_subtitles
            - _titles
            - _subtitles
        """
        self._titles_subtitles = tuple(extract_titles_subtitles(self._path))
        self._titles = tuple(filter(lambda x: x.type == _TYPE_TITLE,
                                    self._titles_subtitles))
        self._subtitles = tuple(filter(lambda x: x.type == _TYPE_SUBTITLE,
                                       self._titles_subtitles))
        self._cached = True

    @property
    def titles(self):
        """All titles extracted from the file speficied by self._path.

        Returns:
            List[TextTypeBboxPageTuple] each of which having its type attribute
            equals _TYPE_TITLE
        """
        if not self._cached:
            self._do_cache()
        return list(self._titles)

    @property
    def subtitles(self):
        """All subtitles extracted from the file speficied by self._path.

        Returns:
            List[TextTypeBboxPageTuple] each of which having its type attribute
            equals _TYPE_SUBTITLE
        """
        if not self._cached:
            self._do_cache()
        return list(self._subtitles)

    @property
    def titles_subtitles(self):
        """A list with titles and subtitles, sorted according to its reading order.
        """
        if not self._cached:
            self._do_cache()
        return list(self._titles_subtitles)

    @property
    def json(self):
        """All titles with its subtitles associated.

        All subtitles under the same title are at the same level.
        Deprecated. Better use `titles_subtitles` or
        `titles_subtitles_hierarchy`.
        """
        if not self._json:
            if not self._cached:
                self._do_cache()
            self._mount_json()
        # return self._json.copy()
        return {k: list(val) for k, val in self._json.items()}

    @property
    def titles_subtitles_hierarchy(self) -> TitlesSubtitles(str, List[str]):
        """All titles and subtitles extracted from the file specified by
        self._path, hierarchically organized.

        Returns:
            List[TitlesSubtitles(str, List[str])]: the titles and its
            respectively subtitles
        """
        if not self._hierarchy:
            if not self._cached:
                self._do_cache()
            self._mount_hierarchy()
        return self._hierarchy.copy()

    def dump_json(self, path):
        """Writes on file specified by path the JSON representation of titles
        and subtitles extracted.

        Dumps the titles and subtitles according to the hierarchy verified
        on the document.

        The outputfile should be specified and will be suffixed with the
        ".json" if it's not.

        Args:
            path: string containing path to .json file where the dump will
            be done. Its suffixed with ".json" if it's not.

        """
        with open(f"{path}{(not path.endswith('.json')) * '.json'}", 'w', encoding='utf-8') as json_file:
            json.dump(self.json,
                      json_file,
                      ensure_ascii=False, indent='  ')

    def reset(self):
        """Sets cache to False and reset others internal attributes.
        Use when for some reason the internal state was
        somehow modified by user.
        """
        self._json = {}
        self._hierarchy = []
        self._cached = False


def gen_title_base(dir_path=".", base_name="titles", indent=4, forced=False):
    """Generates titles base from all PDFs immediately under dir_path directory.
    The base is generated under dir_path directory.
    Args:
        dir_path: path so base_name will contain all titles
            from PDFs under dir_path
        base_name: titles' base file name
        indent: how many spaces used will be used for indent
    Returns:
        dict containing "titles" as key and a list of titles,
            the same stored at base_name[.json]
    """
    base_name = f"{dir_path}/{base_name + (not base_name.endswith('.json')) * '.json'}"
    if os.path.exists(base_name) and not forced:
        print(f"Error: {base_name} already exists")
        return None

    if os.path.isdir(base_name):
        print(f"Error: {base_name} ir a directory")
        return None

    titles = set()
    for file in filter(lambda x: not os.path.isdir(x) and x.endswith('.pdf'), os.listdir(dir_path)):
        extractor = ExtractorTitleSubtitle(file)
        titles_text = map(lambda x: x.text, extractor.titles)
        titles.update(titles_text)
    json_content = {"titles": list(titles)}
    with open(f"{base_name}", 'w', encoding='uft-8') as json_file:
        json.dump(json_content, json_file,
                  ensure_ascii=False, indent=indent*' ')

    return json_content


def gen_hierarchy_base(dir_path=".",
                       folder="hierarchy", indent=4, forced=False):
    """Generates json base from all PDFs immediately under dir_path directory.
    The hiearchy files are generated under dir_path directory.
    Args:
        dir_path: path so folder containing PDFs
        base_name: titles' base file name
        forced: proceed even if folder `base_name` already exists
        indent: how many spaces used will be used for indent

    Returns:
        List[Dict[str, List[Dict[str, List[Dict[str, str]]]]]]
        e.g:
        [
           { "22012019": [
                {
                  "PODER EXECUTIVO": []
                },
                {
                    "SECRETARIA DE ESTADO DE FAZENDA,\nPLANEJAMENTO, ORÇAMENTO E GESTÃO": [
                        {
                            "SUBSECRETARIA DA RECEITA": ""
                        }
                    ]
                }
            }
        ]
        In case of error trying to create `base_name` folder,
        returns None.
    """
    folder = f"{dir_path}/{folder}"
    if not dir_path:
        dir_path = "."
    try:
        os.makedirs(folder, exist_ok=forced)
    except OSError as error:
        print(error)
        return None

    hierarchies = []
    for file in filter(lambda x: x.endswith('.pdf'), os.listdir(dir_path)):
        extractor = ExtractorTitleSubtitle(f"{dir_path}/{file}")
        hierarchy = extractor.titles_subtitles_hierarchy
        hierarchy = [
            ({d[0]: [dict([(i, '')]) for i in d[1]]})
            for d in hierarchy
        ]
        hierarchy = {file.rstrip('.pdf'): hierarchy}
        hierarchies.append(hierarchy)

        with open(f"{folder}/{file.rstrip('.pdf')}.json", 'w', encoding='utf-8') as json_path:
            json.dump(hierarchy,
                      json_path,
                      ensure_ascii=False, indent=indent*' ')

    return hierarchies
