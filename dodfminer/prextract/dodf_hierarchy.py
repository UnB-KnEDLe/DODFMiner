"""."""

import os
import re
import json
import operator
from itertools import chain
from typing import List, Iterable, Tuple

import fitz
import prextract.title_filter as title_filter

_TYPE_TITLE, _TYPE_SUBTITLE = "title", "subtitle"
_TITLE_MULTILINE_THRESHOLD = 10
_TRASH_EXPRESSIONS = [
    "SUMÁRIO",
    "DIÁRIO OFICIAL",
    "SEÇÃO (I|II|III)",
    "SEÇÃO",
]

_TRASH_COMPILED = re.compile('|'.join(_TRASH_EXPRESSIONS))


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


def is_bold(flags):
    return flags & 2 ** 4

# def is_bold(flags):
#     return flags in [16, 20]


def reading_sort(lis):
    """Returns `lis` sorted according to reading order.

    Assumes `lis` elements are disposed on a 1-column layout and sort them according
    to page number and vertical coordinate. Therefore, tries to resemble natural
    reading order.

    Args:
        lis: List[Dict], each dict gaving at least `page` and `bbox` keys.
            `page` should have an positive integer as value and `page` tuple
            whose second element refers to vertical location on page
            (assuming bottom having BIGGER values.)
    Returns:
        the list of elements received, now in natural reading order.  
    """
    return sorted(lis, key=lambda x: (x['page'], int(x['bbox'][1]), x['bbox'][0]))


def get_spans_by_page(doc):
    """ Extracts text spans ("lines) inside file on `path`.
    
    Returns:
        List[List[[bbox, color, flags, font, page, size, text]]]
        (list of all spans extracted from file of path each of which
        as SimpleNamespace instead of dict instances)
    """
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
    return blocos


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
        # Is top-left corner on left [horizontal] half of the page?
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


def remove_header_footer(lis):
    y0l = [ x['bbox'][1] for x in lis ]
    mi, ma = min(y0l), max(y0l)
    idx_mi, idx_ma = y0l.index(mi), y0l.index(ma)
    left, right = min(idx_mi, idx_ma), max(idx_mi, idx_ma)
    del lis[left]
    del lis[right-1]
    return lis

def drop_header_footer(lis: List[tuple]):
    y0l = [ x.y0 for x in lis ]
    mi, ma = min(y0l), max(y0l)
    idx_mi, idx_ma = y0l.index(mi), y0l.index(ma)
    left, right = min(idx_mi, idx_ma), max(idx_mi, idx_ma)
    del lis[left]
    del lis[right-1]
    return lis


class DocumentDODF(fitz.Document):
    """Specialized class of fitz.Document designed to be used on DODF files.
    """
    def __init__(self, filename=None, stream=None, filetype=None, rect=None, width=0, height=0, fontsize=11):
        super().__init__(filename, stream, filetype, rect, width, height, fontsize)
        # Turning left columns into even and right ones into odd before
        # sorting to natural reading order
        # self._spans = reading_sort(page_transform(get_spans_by_page(self)))
        # self._spans = [reading_sort(ii) for ii in \
        #     (page_transform(i) for i in get_spans_by_page(self))            
        # ]

        self._spans = [reading_sort(ii) for ii in \
            (page_transform( remove_header_footer(i) ) for i in get_spans_by_page(self))            
        ]
        self._text_blocks = self.getTextBlocksNoFooter()
    
    def __repr__(self):
        m = "closed " if self.isClosed else ""
        if self.stream is None:
            if self.name == "":
                return m + "DocumentDODF[fitz.Document](<new PDF, doc# %i>)" % self._graft_id
            return m + "DocumentDODF[fitz.Document]('%s')" % (self.name,)
        return m + "DocumentDODF[fitz.Document]('%s', <memory, doc# %i>)" % (self.name, self._graft_id)

    def getTextBlocks(self):
        """Convenivence function to get all text blocks from a document.
        Returns:
            a list of tuples with the following format:
                (x0, y0, x1, y1, "lines in blocks", block_type, block_no, page_no, page_width)
        """
        l = []
        for idx, p in enumerate(self):
            l.append(
                [{**BlockToDict(bl), 'page_width': p.MediaBox[2], 'page': idx } for bl in p.getTextBlocks()]
            )
        return l

    def getTextBlocksNoFooter(self):
        """Convenivence function to get all text blocks from a document, except by footers and headers.
        Returns:
            a list of tuples with the following format:
                (x0, y0, x1, y1, "lines in blocks", block_type, block_no, page_no, page_width)
        """
        l = []
        for idx, p in enumerate(self):
            l.append( reading_sort(page_transform(remove_header_footer(
                [{**BlockToDict(bl), 'page_width': p.MediaBox[2], 'page': idx } for bl in p.getTextBlocks()]
            ))))
        return l

    @property
    def spans(self, idx=None):
        if idx == None:
            return self._spans
        else:
            return self._spans[idx]
        # return [dic.copy() for dic in self._spans] if idx0 is None else self._spans[idx0].copy()

    @property
    def text_blocks(self, idx=None):
        return [dic.copy() for dic in self._text_blocks] if idx is None else self._text_blocks[idx].copy()



def is_title_subtitle(span):
    return ((title_filter.BoldUpperCase.dict_text(span))
            and is_bold(span['flags'])
            and not re.search(_TRASH_COMPILED, span['text'])
            and 'calibri' not in span['font'].lower()
        )


def are_title_subtitle(span_list):
    return [is_title_subtitle(span) for span in span_list]


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


def get_block_spans(block): 
    span_lis = [] 
    for line in block['lines']: 
        for span in line['spans']: 
            span_lis.append(span) 
    return span_lis


def get_titles_candidates(span_lis):
    cand = []
    for idx, span in enumerate(span_lis):
        t = span['text']
        if not re.search(_TRASH_COMPILED, t) and t.upper() == t:
            span.append(idx)
    return cand


def get_title_boxes_candidates(block_tuple_list):
    return [i for i in block_tuple_list if i[4] == i[4].upper()]

def get_upper_text_blocks(text_blocks):
    return [i for i in text_blocks if i[4] == i[4].upper()]


def get_span_title_candidates(page: fitz.Page = None):
    """Returns list of indexes of `page.getTextBlocks` [sub]title candidates.
    """
    doc=fitz.open('2.pdf')
    text_blocks = page.getTextBlocks()
    page_blocks = page.getTextPage().extractDICT()['blocks']  
    block_and_idx = [] 
    for tup in text_blocks:
        idx = tup[5]
        block = page_blocks[idx] 
        block_and_idx.append((block, idx)) 
    block_upper_id = []
    for block, block_idx in block_and_idx:
        if are_title_subtitle(get_block_spans(block)): 
            block_upper_id.append(block_idx) 
    ret = []
    for idx in block_upper_id:
        spans = get_block_spans( page_blocks[idx]) 
        if all(are_title_subtitle(span_list=spans)): 
            # print('Block: {}', idx, spans, sep='  ')
            ret.append(idx)
    return ret


def show_page_text_blocks_title_candidates(page: fitz.Page, cand_idx):
    text_blocks = page.getTextBlocks()
    for idx in cand_idx:
        print('>', text_blocks[idx])
    

def show_page_spans_title_candidates(page: fitz.Page, cand_idx):
    text_blocks = page.getTextPage().extractDICT()['blocks']
    for idx in cand_idx:
        print('>', text_blocks[idx])
    

# def mount_hierarchy():


# if __name__ == '__main__':
#     pass

#     doc = DocumentDODF(path)


#     text_blocks = DocumentExt(path).getTextBlocks()
#     text_spans = get_pdf_spans(path)

#     list_blocks = list(chain(*text_blocks))

#     list_spans = list(chain(*text_spans.values()))
#     list_spans = sorted(list_spans, key=lambda x: (x['page'], x['bbox'][1]))

#     passed=0

#     lim=len(text_spans)
#     idx_spans = 0
#     ll = []
#     for block in list_blocks:
#         l = []
#         block_rect = fitz.Rect(block[:4])
#         while fitz.Rect( list_spans[idx_spans]['bbox'] ) in block_rect:
#         l.append(list_spans[idx_spans]['text'])
#         idx_spans += 1
#         if not l:
#             print("SEM SPAN : ", block[4])
#             input()
#         ll.append(l)
        
# upper_by_page=[get_upper_text_blocks(j.getTextBlocks()) for j in doc] 
# page_blocks = doc[0].getTextPage().extractDICT()['blocks']
# for tup in upper_by_page[0]: 
#     print(page_blocks[tup[5]]) 
#     print('-------------------------') 
     
 
