"""."""

import os
import re
import json
import operator
from itertools import chain
from typing import List, Iterable, Tuple

import fitz
import title_filter

def BlockToDict(block):
    """Converts pymupdf `block` tuple to dictionary.
    A convenience function to standarize with `spans` returned by
        fitz.TextPage.extractDICT().
    Args:
        block: Tuple[float, float, float, float, str, int, int]
    """
    d = {}
    d['bbox'] = tuple([*block[:4]])
    d['text'] = block[4]
    d['block_no'] = block[-1]
    return d

def flags_decomposer(flags):
    """Make font flags human readable."""
    l = []
    if flags & 2 ** 0:
        l.append("superscript")
    if flags & 2 ** 1:
        l.append("italic")
    if flags & 2 ** 2:
        l.append("serifed")
    else:
        l.append("sans")
    if flags & 2 ** 3:
        l.append("monospaced")
    else:
        l.append("proportional")
    if flags & 2 ** 4:
        l.append("bold")
    return ", ".join(l)


def is_bold(flags):
    return flags & 2 ** 4

_TRASH_EXPRESSIONS = [
    "SUMÁRIO",
    "DIÁRIO OFICIAL",
    "SEÇÃO (I|II|III)",
]

_TRASH_COMPILED = re.compile('|'.join(_TRASH_EXPRESSIONS))

_TYPE_TITLE, _TYPE_SUBTITLE = "title", "subtitle"
_TITLE_MULTILINE_THRESHOLD = 10


def get_text_spans(path):
    """ Extracts text spans ("lines) inside file on `path`.
    
    Returns:
        List[Dict[bbox, color, flags, font, page, size, text]]
        (list of all spans extracted from file of path each of which
        as SimpleNamespace instead of dict instances)
    """
    doc = fitz.open(path)
    blist = [p.getTextPage().extractDICT()['blocks'] for p in doc]

    blocos = []
    for page, lis in enumerate(blist):
        page_width = doc[page].MediaBox[2]
        tmp = [] 
        for bl in lis:  
            for line in bl['lines']: 
                for sp in line['spans']: 
                    tmp.append( dict(**sp, page=page, page_width=page_width) )
        blocos.append(tmp) 
    return list(chain(*blocos))


def page_transform(blocks, keep_page_width=True, inplace=False):
    """Increases page numbers of blocks.
        This function takes an list of dictionaries each of wich
        having at least 'page', 'page_width' and 'bbox' as keys,
        and modify 'page' entry if bbox[0] > page_width / 2.
        Basically, "stacks" text based first on page and then if it is
        located on left/right half-horizontal.


    Args:
        blocks: List[Dict]
        keep_page_width: whether to drop or not `page_width`
            dict entries
    Returns:
        the modified list.
    WARNING:
        blocks is modified.
    """
    if not inplace:
        blocks = [i.copy() for i in blocks]
    for d in blocks:
        p_num = d['page']
        p_width = d.pop('page_width') if \
                    not keep_page_width else d['page_width']
        p_num *= 2
        x0, y0, x1, y1 = d['bbox']
        p_num += int(x0 >( p_width / 2))
        # p_num = p_num + int(((x0 > p_width/2) and (x1 > p_width/2) ))
        # p_num = p_num + int(x0 > (p_width * .4) and x1 > (p_width / 2))
        d['page'] = p_num
    return blocks


def group_by(lis, key):
    keys = set( (i[key] for i in lis) )
    grouped = dict.fromkeys(sorted(keys), None )
    for k, v in grouped.items(): grouped[k] = []
    for el in lis:
        grouped[el['page']].append(el)
    return grouped


def get_pdf_spans(path):
    """
  
    Returns:
        Dict[int -> List]
    """
    return group_by(
      page_transform(
        get_text_spans(path)),
        key='page'
      )

class DocumentDODF(fitz.Document):
    """Specialized class of fitz.Document designed to be used on DODF files.
    """
    def __init__(self, filename=None, stream=None, filetype=None, rect=None, width=0, height=0, fontsize=11):
        super().__init__(filename, stream, filetype, rect, width, height, fontsize)
        _ = list(chain(*self.getTextBlocks()))
        # Turning left columns into even and right ones into odd
        _ = page_transform(_, keep_page_width=False, inplace=True)
        # Attempt to do it stay in natural reading order
        _ = sorted(_, key=lambda x: (x['page'], x['bbox'][1]))
        self._text_blocks = _
        _ = list(chain(*get_pdf_spans(filename).values()))
        _ = page_transform(_, keep_page_width=False, inplace=True)
        _ = sorted(_, key=lambda x: (x['page'], x['bbox'][1]))
        self._spans = _
    
    def getTextBlocks(self):
        """
        Returns:
            a list of tuples with the following format:
                (x0, y0, x1, y1, "lines in blocks", block_type, block_no, page_no, page_width)
        """
        l = []
        for idx, p in enumerate(self):
            tmp = p.getTextBlocks()
            tmp = [{**BlockToDict(bl), 'page_width': p.MediaBox[2], 'page': idx } for bl in tmp]
            l.append( tmp )
        return l


    @property
    def spans(self, idx=None):
        return self._spans if idx is None else self._spans[idx]


def get_titles_subtitles_smart(path):
    """Extracts titles and subtitles. Makes use of heuristics.

    Wraps _get_titles_subtitles, removing most of impurity
    (spans not which aren't titles/subtutles).
    
    Args:
        path: str with the path do DODF PDF file

    Returns:
        TitlesSubtitles(List[TextTypeBboxPageTuple], List[TextTypeBboxPageTuple]).
    """
    bold_spans = list(chain(*get_pdf_spans(path).values()))
    filtered1 = filter(title_filter.BoldUpperCase.dict_text, bold_spans)
    filtered2 = filter(lambda s: not re.search(_TRASH_COMPILED, s['text']), filtered1)
    # 'calibri' as font apears sometimes, however never in titles or subtitles
    filtered3 = filter(lambda x: 'calibri' not in x['font'].lower(), filtered2)
    filtered4 = filter(lambda x:  is_bold(x['flags']), filtered3)
    return list(filtered4)


doc = DocumentDODF(path)




text_blocks = DocumentExt(path).getTextBlocks()
text_spans = get_pdf_spans(path)

list_blocks = list(chain(*text_blocks))

list_spans = list(chain(*text_spans.values()))
list_spans = sorted(list_spans, key=lambda x: (x['page'], x['bbox'][1]))

passed=0

lim=len(text_spans)
idx_spans = 0
ll = []
for block in list_blocks:
    l = []
    block_rect = fitz.Rect(block[:4])
    while fitz.Rect( list_spans[idx_spans]['bbox'] ) in block_rect:
      l.append(list_spans[idx_spans]['text'])
      idx_spans += 1
    if not l:
        print("SEM SPAN : ", block[4])
        input()
    ll.append(l)
    



if __name__ == '__main__':
  pass