#!/usr/bin/env python
# coding: utf-8

# In[1]:

# %load_ext autoreload
# %autoreload 2

# In[26]:

import re
import json
import os
from typing import List, Dict, Union, NamedTuple, Tuple
from pathlib import Path

import fitz
import dodfminer.prextract.title_filter as title_filter

# In[30]:
class TextBlockTrans(NamedTuple):
    x0: float
    y0: float
    x1: float
    y1: float
    text: str
    block_no: int
    page: int
    pwidth: float = None
    def __repr__(self):
        ret = []
        ret.append('TextBlockTrans')
        ret.append('\tbbox: ({}, {}, {}, {})'.format(*self[:4]))
        ret.append('\ttext: {}'.format(self.text))
        ret.append('\tblock_no: {}'.format(self[5]))
        ret.append('\tpage, pwidth: {}'.format(self[-2:]))
        return '\n'.join(ret)

_TRASH_EXPRESSIONS = [
    "SUMÁRIO",
    "DIÁRIO OFICIAL",
    "SEÇÃO (I|II|III)",
]
_TRASH_COMPILED = re.compile('|'.join(_TRASH_EXPRESSIONS))


def is_bold(flags):
    return flags & 2 ** 4

def textBlock_to_textblocktrans(lis: List[Tuple[float, float, float, float, str, int, int]], page_width, pnum):
    """Given a text_block list (of tuples), return one with 
    two more values at the end, indicating `page number` and
    `page width`.
    WARNING: the old last value is dropped (usually its
    the type of block, but since always it seems to be the same value,
    no information if brought).
    """
    return [TextBlockTrans(*i[:-1], pnum, page_width) for i in lis]


def page_transform(extracted_blocks, keep_page_width=True, inplace=False):
    """Increases page numbers of extracted_blocks.
        This function takes an list of dictionaries each of wich
        having at least 'page', 'page_width' and 'bbox' as keys,
        and modify 'page' entry if bbox[0] > page_width / 2.
        Basically, "stacks" text based first on page and then if it is
        located on left/right half-horizontal.

    Args:
        extracted_blocks: List[Dict]
        keep_page_width: whether to drop or not `page_width`
            dict entries
    Returns:
        the modified list.
    WARNING:
        extracted_blocks is modified.
    """
    if not inplace:
        extracted_blocks = [i.copy() for i in extracted_blocks]
    for d in extracted_blocks:
        p_num = d['page']
        p_width = d.pop('page_width') if not keep_page_width else d['page_width']
        p_num *= 2
        x0, y0, x1, y1 = d['bbox']
        # Is top-left corner on left [horizontal] half of the page?
        p_num += int( x0 >( p_width / 2))
        d['page'] = p_num
    return extracted_blocks


def text_blocks_transform(text_blocks: List, keep_page_width=True):
    """Similar to `page_transform`.

    Do the same as `page_transform` but `text_blocks` is expected to
    contain `TextBlockTrans` instances insted of `dict` instances as
    in `page_transform`. A big difference is the list returned, which
    is NOT the same as `text_blocks`.
    """
    lis = []
    for idx, tb in enumerate(text_blocks):
        p_num = tb.page
        p_width = tb.pwidth

        p_num *= 2
        p_num += int(tb.x0 > (p_width / 2))
        if keep_page_width:            
            lis.append( TextBlockTrans( *(tb[:-2]), p_num, p_width ) )
        else:
            lis.append( TextBlockTrans( *(tb[:-2]), p_num, ) )
    return lis


def is_title_subtitle(span):
    """Evaluates to True if span['text'] is a title or subtitle.

    Args:
        span: `dict` with keys ('flags', 'text', 'font')
    Returns:
        True if span['text'] can be part of a title or subtitle.
        False otherwise.
    """
    return ((title_filter.BoldUpperCase.dict_text(span))
            and is_bold(span['flags'])
            and not re.search(_TRASH_COMPILED, span['text'])
            and 'calibri' not in span['font'].lower()
        )

def are_title_subtitle(span_list):
    """Convenince function to apply `is_title_subtitle` over an iterable.
    Args:
        span_list: an iterable of `dict` each of which having the same keys
            expected by `is_title_subtitle`
    Returns:
        a `list` containing the results of applying `is_title_subtitle`
        on each element in `span_list`.
    """
    return [is_title_subtitle(span) for span in span_list]

def get_block_spans(block):
    """Returns all spans giver a block (a `block` as returned by fitz.TextPage.extractDICT).

    Args:
        block: text block as described at https://pymupdf.readthedocs.io/en/latest/textpage/#dictionary-structure-of-extractdict-and-extractrawdict
    Returns:
        all `spans` inside `block`
    """
    span_lis = [] 
    for line in block['lines']: 
        for span in line['spans']: 
            span_lis.append(span) 
    return span_lis

def reading_sort_tuple(lis):
    return sorted(lis, key=lambda x: (x.page, int(x.y0), x.x0))

def reading_sort_dict(lis):
    return sorted(lis, key=lambda x: (x['page'], int(x['bbox'][1]), x['bbox'][0]))

def drop_dup_tbt(lis: List[TextBlockTrans]):
    """Assumes elements with same (int(x0), int(y0)) coordinates are the same and keeps only one.
    

    Sometimes, a span text apears multiple times, as if there exists
    multiple spans starting at the same point. Tihs function drops
    duplicate which matches this case.
    Args:
        lis: a sequence of `TextBlockTrans` instances
    Returns:
        a `list` removing duplicated (as defined above) instances.

    NOTE: please note that all `lis` elements are assumed to be on the SAME page.
    If this is not the case, then the final result may not be what was expected.
    """
    dic = {}
    for tup in lis:
        dic[tuple([int(i) for i in tup[:2]])] = tup
    return list(dic.values())


def drop_header_footer_smart(lis: List[tuple], page_height=None, page_width=None):

    if not lis:         # Some pages for some reason are empty
        return lis

    y0l = [ x.y0 for x in lis ]
    mid_width = page_width/2
    mid_height = page_height/2
    shrinked = False
    if len(lis) > 1:
        mi = min(y0l)
        idx_mi = y0l.index(mi)
        high = lis[idx_mi]
        cond1 = high.x0 < mid_width
        cond2 = high.x1 > mid_width
        cond3 = 'Diário Oficial do Distrito Federal' in high.text
        # cond4 = .19 < (high.y0 / page_height) < .22
        if cond1 and cond2 and cond3:
            shrinked = True
            del lis[idx_mi]
    if len(lis) > 1:
        ma = max(y0l)
        # As noticed, this rate keeps for footer or poor-formated text.
        # If for any reason the last case occurs, unfortunately
        # the footer will be kept.
        if ma / page_height > .95:
            # pass
            ma_idx = y0l.index(ma)
            # If ma_idx ==0, then ok. Else, once list 
            # may have been shrinked and this must be taken
            # into account.
            del lis[ma_idx if not ma_idx else ma_idx - shrinked]

    # NOTE: it is possible to do the check for header and footer
    # nearly using only text. However, it is computationally
    # expensive.
    return lis


def get_first_title_cands(extracted_blocks, page_width):
    """Returns first_title candidates.
    """
    extracted_blocks = [{**b, 'page': 0, 'page_width': page_width} for b in extracted_blocks]
    extracted_blocks = reading_sort_dict(page_transform(extracted_blocks))
    sps = []
    for block in extracted_blocks:
        for line in block['lines']:
            for sp in line['spans']:
                sps.append(sp)
    cands = [(idx, sp) for (idx, sp) in enumerate(sps) if (
        re.sub(r'[ \n]+', '', sp['text']).startswith('SEÇÃOI') \
        and is_bold(sp['flags']) \

    )]
    # Unfortunately, some older PDF files has "SEÇÃO I" in bold fonts
    # Proposed solution: sort candidates by decreasing font size

    # What if firt section is not "SEÇÃO I"? Then, "SEÇÃO ..." 
    # with the small length should be choosen
    # cands = sorted(cands, key=lambda x: (x[1]['size'], -len(x[1]['text']) ), reverse=True)

    cands = sorted(cands, key=lambda x: x[1]['size'], reverse=True)
    return sps, cands


def init_hier_final(doc: fitz.Document):

    spans, candidates = get_first_title_cands(
        extracted_blocks=doc[0].getTextPage().extractDICT()['blocks'],
        page_width=doc[0].MediaBox[2],
    )
    sp = spans[candidates[0][0] + 1]
    title_size = sp['size']
    print("\t[init_hier] first_title of {}: {} - Size: {}".format(
        doc.name, sp['text'], title_size
    ))
    current_section = 'SEÇÃO 0'
    hier = {
        current_section: [
            [
                ['preambulo'],
                []
            ]
        ]
    }

    return current_section, hier, title_size


def new_subtitle(text=''):
    return (
        [
            [text],         # subtitles (text)
            []              # text blocks (TextBlockTrans)
        ]
    )


def new_title(text=''):
    return    [ 
        [text],  # titles (text)
        [
            # subtitles (text)
            # text blocks (TextBlockTrans)
        ]
    ]


def mount_hierarchy(doc: fitz.Document, possile_section_debug=False, section_debug=False):
    """Mounts DODF document hierarchy (secao, titulo, subtitulo and textblocks).

    Receives an `fitz.Document` instance, `doc`. Then that function will try to 
        re-assembly the original hierarchy w.r.t (secao, titulo, subtitulo, textblocks)
    Returns:
        Dict[str, List[List[str, List[str]]]]

    """
    current_section_idx, hier, TITLE_SIZE = init_hier_final(doc)
    prev_font_size = 0
    prev_spans = []
    for p_num, page in enumerate(doc):
        p_width = page.MediaBox[2]

        text_blocks = page.getTextBlocks()
        extracted_blocks = page.getTextPage().extractDICT()['blocks']

        tb_paged = textBlock_to_textblocktrans(text_blocks, p_width, p_num)    
        tb_trans = text_blocks_transform(tb_paged, keep_page_width=False)

        cleaned_and_sorted = drop_header_footer_smart(
            reading_sort_tuple(
                drop_dup_tbt(
                    tb_trans
                )
            ),
            page_height=page.MediaBox[3],
            page_width=page.MediaBox[2]
        )

        for text_block in cleaned_and_sorted:

            spans = [sp for sp in get_block_spans(extracted_blocks[text_block.block_no]) if len(sp['text']) > 1]
            if not spans:
                continue
            # `page_transform` espera que as chaves `page` e `page_width` existam.
            for sp in spans:
                sp['page'] = p_num
                sp['page_width'] = doc[p_num].MediaBox[2]
            # `reading_sorts`espera que haja chave `page`, além de `bbox`
            spans = reading_sort_dict(page_transform(spans))
            first = spans[0]
            first_size = first['size']         
            first_text = first['text']
            if possile_section_debug and first_text.startswith('SEÇÃO'):    print("\033[92m possivel seção: ", first_text, "\033[0m")

            if is_bold(first['flags']) \
                and text_block.text.startswith('SEÇÃO I') and text_block.text.endswith('I'):
                if section_debug:   print('SEÇÃO: \n\t"{}"'.format(first))
                current_section_idx = first_text
                hier[current_section_idx] = []
                continue

            not_fake = [ not re.match(_TRASH_COMPILED, sp['text']) for sp in spans]
            section = hier[current_section_idx]

            if all(are_title_subtitle(spans)) and first_size == TITLE_SIZE and all(not_fake):  # 
                if first_size == prev_font_size:                    
                    section[-1][0].append(text_block.text)
                else:   # Title doesn't extend the previous one
                    section.append(new_title(text_block.text))                
            
            else:   # another block inside a title. Check if `first` has bold font.
                    # If is has then a subtitle is assumed.
                for sp in spans:
                    txt = sp['text']
                    if is_bold(sp['flags']) and not re.match(_TRASH_COMPILED, sp['text'])\
                        and sp['size'] < TITLE_SIZE and txt == txt.upper() : # subtitle
                        if prev_font_size != sp['size']:
                            section[-1][1].append(new_subtitle())
                            prev_font_size = sp['size']
                        section[-1][1][-1][0].append(txt)
                    else:   # remaining spans are [assumed to be] ordinary ones. TODO: elaborate.
                        break
                if not section[-1][1]:
                    section[-1][1].append(new_subtitle())
                section[-1][1][-1][1].append(text_block.text)
            prev_font_size = spans[-1]['size']
            prev_spans = spans.copy()
    return hier


def post_process_hierarchy(hierarchy: dict):
    for k, v in hierarchy.items():
        for (idx, (title_parts, rest)) in enumerate(v):
            v[idx][0] = '\n'.join((i for i in v[idx][0] if i))
            for (idx2, (subtitle_parts, text_blocks)) in enumerate(rest):
                rest[idx2][0] = '\n'.join((i for i in rest[idx2][0] if i))
    return hierarchy


def show_post_hier(hierarchy: dict):
    for k, v in hierarchy.items(): 
        print('\033[1m', k, ' ------>\n') 
        for title, rest in v: 
            print('\033[94m\t',title.replace('\n', ' ')) 
            for subtitle, blocks in rest: 
                if subtitle: 
                    print('\033[92m\t\t', subtitle.replace('\n', ' ')) 
                else:
                    print('\033[92m\t\t<no-subtitle>')
            print() 
        print('\033[0m')    


if __name__ == '__main__':
    TEST_PATH = Path('PDF_TITLES/')
    TEST_FILES = [TEST_PATH/Path(path) for path in os.listdir(TEST_PATH) if path.endswith('.pdf')]
    PATH = TEST_FILES[0]
    doc = fitz.open(PATH)

    sps, cands = get_first_title_cands(
        doc[0].getTextPage().extractDICT()['blocks'],
        doc[0].MediaBox[2],
    )

    print(*cands, sep='\n\n')

    print('SEÇÃO I --> ', sps[cands[0][0]])
    print('TÍTULO I --> ', sps[cands[0][0]+1])

    bls = doc[0].getTextPage().extractDICT()['blocks']
    page_width = doc[0].MediaBox[2]
    sps, cands = get_first_title_cands(bls, page_width)
    del bls, page_width

    print('candidades:', cands)
    print('most-likely:', sps[cands[0][0]+1])

    for filename in TEST_FILES:
        # try:
        # h, dbg = mount_doc_hierarchy2(fitz.open(filename))
        h = mount_hiearchy(fitz.open(filename))
        ph = post_process_hierarchy(h)
        json.dump(
            ph, open(str(filename)[:-4]+'_hierarchy_full.json' ,'w'),
            ensure_ascii=False, indent=4*' '
        )
        print('\t', filename, 'OK')
