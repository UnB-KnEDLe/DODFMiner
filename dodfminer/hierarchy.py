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
import prextract.title_filter as title_filter


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



TEST_PATH = Path('PDF_TITLES/')
TEST_FILES = [TEST_PATH/Path(path) for path in os.listdir(TEST_PATH) if path.endswith('.pdf')]
PATH = TEST_FILES[0]
_TRASH_EXPRESSIONS = [
    "SUMÁRIO",
    "DIÁRIO OFICIAL",
    "SEÇÃO (I|II|III)",
]

_TRASH_COMPILED = re.compile('|'.join(_TRASH_EXPRESSIONS))


print('PDF file:', PATH)
doc = fitz.open(PATH)


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


def text_blocks_transform(text_blocks: List, keep_page_width=True):
    lis = []
    for idx, tb in enumerate(text_blocks):
        p_num = tb[-2]
        p_num = tb.page
        
        
        p_width = tb[-1]
        p_width = tb.pwidth
        
        
        p_num *= 2
        x0, y0, x1, y1 = tb[:4]
        x0 = tb.x0
        
        p_num += int(x0 >( p_width / 2))
        if keep_page_width:            
            lis.append( TextBlockTrans( *(tb[:-2]), p_num, p_width ) )
        else:
            lis.append( TextBlockTrans( *(tb[:-2]), p_num, ) )
    return lis


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
        p_width = d.pop('page_width') if not keep_page_width else d['page_width']
        p_num *= 2
        x0, y0, x1, y1 = d['bbox']
        # Is top-left corner on left [horizontal] half of the page?
        p_num += int( x0 >( p_width / 2))
        d['page'] = p_num
    return blocks


def is_title_subtitle(span):
    return ((title_filter.BoldUpperCase.dict_text(span))
            and is_bold(span['flags'])
            and not re.search(_TRASH_COMPILED, span['text'])
            and 'calibri' not in span['font'].lower()
        )


def are_title_subtitle(span_list):
    return [is_title_subtitle(span) for span in span_list]



def get_block_spans(block):
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
    """. This fun
    
    Sometimes, a span text apears multiple times, as if there exists
    multiple spans starting at the same point. Tihs function drops
    duplicate which matches this case.
    """
    dic = {}
    for tup in lis:
        dic[tuple([int(i) for i in tup[:2]])] = tup
    return list(dic.values())


def drop_header_footer(lis: List[tuple]):
    y0l = [ x.y0 for x in lis ]
    mi, ma = min(y0l), max(y0l)
    idx_mi, idx_ma = y0l.index(mi), y0l.index(ma)
    left, right = min(idx_mi, idx_ma), max(idx_mi, idx_ma)
    del lis[left]
    del lis[right-1]
    return lis


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

    # NOTE: it is possible to do the check for header em footer
    # nearly using only text. However, it is computationally
    # expensive.
    return lis


def get_first_title_cands(extract_blocks, page_width):
    """Returns first_title candidates.
    """
    extract_blocks = [{**b, 'page': 0, 'page_width': page_width} for b in extract_blocks]
    extract_blocks = reading_sort_dict(page_transform(extract_blocks))
    sps = []
    for block in extract_blocks:
        for line in block['lines']:
            for sp in line['spans']:
                sps.append(sp)
    cands = [(idx, sp) for (idx, sp) in enumerate(sps) if (
        re.sub(r'[ \n]+', '', sp['text']) == 'SEÇÃOI' \
        and is_bold(sp['flags']) \
        
    )]
    # Unfortunately, some older PDF files has "SEÇÃO I" in bold fonts
    # Proposed solution: sort candidates by decreasing font size
    cands = sorted(cands, key=lambda x: x[1]['size'], reverse=True)
    return sps, cands


def mount_doc_hierarchy(doc: fitz.Document):

    spans, candidates = get_first_title_cands(
        doc[0].getTextPage().extractDICT()['blocks'],
        doc[0].MediaBox[2],
    )

    sp = spans[candidates[0][0] + 1]
    print('first title: ', sp['text'])
    input()
    
    TITLE_SIZE = sp['size']
        
    prev_font_size = 0
    hier = [ (['preambulo'], []) ]
    
    _dbg = []
    prev_spans = []
    for idx, page in enumerate(doc):
        _dbg.append([])
        p_width = page.MediaBox[2]

        text_blocks = page.getTextBlocks()
        extract = page.getTextPage().extractDICT()['blocks']

        if len(text_blocks) != len(extract):
            raise ValueError("different blocks len! {} vs {}".format(
                len(text_blocks), len(extract)))

        tb_paged = textBlock_to_textblocktrans(text_blocks, p_width, idx)    
        tb_trans = text_blocks_transform(tb_paged, keep_page_width=False)

        # cleaned_and_sorted = drop_header_footer(
        cleaned_and_sorted = drop_header_footer_smart(
            reading_sort_tuple(
            drop_dup_tbt(
                tb_trans
            )),
            page_height=page.MediaBox[3],
            page_width=page.MediaBox[2]
        )

        for text_block in cleaned_and_sorted:
            spans = get_block_spans(extract[text_block.block_no])
            
            if not spans:
                raise ValueError(
                    "This message should never be shown. spans: {}".format(
                        spans))
                continue

            for sp in spans:
                sp['page'] = idx
                sp['page_width'] = doc[idx].MediaBox[2]
            
            spans = reading_sort_dict(page_transform(spans))
            
            _dbg[-1].extend(spans)
            
            assert text_block[:4] == extract[text_block.block_no]['bbox']
            
            first = spans[0]
            
            # Title false potive [?]
            if first['text'].startswith('SEÇÃO I') and is_bold(first['flags']):
                print("SEÇÃO I[...] ?")
                print(first)
                # end of section
                # TODO: organize titles by sections.
                # LIMITATIONS: olders PDFs 
                # (multiplie bold "SEÇÃO I" should not work)
                continue
            
            first_size = first['size']
            
            # Temos um título?
            cond1 = bool(spans)

            # TODO: use condition in nested if, so that subtitles
            # are not treated as simple text
            cond3 = first_size == TITLE_SIZE
            
            not_fake = [ not re.match(_TRASH_COMPILED, sp['text']) for sp in spans]            
            if cond1 and all(are_title_subtitle(spans)) and cond3 and all(not_fake):
                # verificar se não estende o anterior (múltiplas linhas)
                if first_size == prev_font_size and hier[-1][0][0] != 'preambulo':
                    # Multi-line titles
                    print("EXTENDING {} BY {}".format(hier[-1][0], text_block.text))
                    hier[-1][0].extend([text_block.text])
                else:
                    last = hier[-1]
                    hier[-1] = ('\n'.join(last[0]), last[1])
                    hier.append( ([text_block.text], []) )                
            else:  # another block inside a title
                hier[-1][1].append(text_block)
            prev_font_size = spans[0]['size']
            prev_spans = spans.copy()
    
    hier[-1] = ('\n'.join(hier[-1][0]), hier[-1][1])
    return hier, _dbg


def mount_doc_hierarchy2(doc: fitz.Document):

    spans, candidates = get_first_title_cands(
        doc[0].getTextPage().extractDICT()['blocks'],
        doc[0].MediaBox[2],
    )

    sp = spans[candidates[0][0] + 1]
    print('first title: ', sp['text'])
    input()
    
    TITLE_SIZE = sp['size']
        
    prev_font_size = 0

    hier = {}
    current_section = 'SEÇÃO 0'

    hier[current_section] = [(['preambulo'], [])]

    
    _dbg = []
    prev_spans = []
    for idx, page in enumerate(doc):
        _dbg.append([])
        p_width = page.MediaBox[2]

        text_blocks = page.getTextBlocks()
        extract = page.getTextPage().extractDICT()['blocks']

        if len(text_blocks) != len(extract):
            raise ValueError("different blocks len! {} vs {}".format(
                len(text_blocks), len(extract)))

        tb_paged = textBlock_to_textblocktrans(text_blocks, p_width, idx)    
        tb_trans = text_blocks_transform(tb_paged, keep_page_width=False)

        # cleaned_and_sorted = drop_header_footer(
        cleaned_and_sorted = drop_header_footer_smart(
            reading_sort_tuple(
            drop_dup_tbt(
                tb_trans
            )),
            page_height=page.MediaBox[3],
            page_width=page.MediaBox[2]
        )

        for text_block in cleaned_and_sorted:

            spans = get_block_spans(extract[text_block.block_no])
            
            if not spans:
                raise ValueError(
                    "This message should never be shown. spans: {}".format(
                        spans))
                continue

            for sp in spans:
                sp['page'] = idx
                sp['page_width'] = doc[idx].MediaBox[2]
            
            spans = reading_sort_dict(page_transform(spans))
            
            _dbg[-1].extend(spans)
            
            assert text_block[:4] == extract[text_block.block_no]['bbox']
            
            first = spans[0]
            
            # Title false potive [?]
            first_text = first['text'] 
            if first_text.startswith('SEÇÃO I') and first_text.endswith('I') and is_bold(first['flags']):
                print("SEÇÃO I[...] ?")
                print(first)
                current_section = first_text
                hier[current_section] = []
                # end of section
                # TODO: organize titles by sections.
                # LIMITATIONS: olders PDFs 
                # (multiplie bold "SEÇÃO I" should not work)
                continue
            del first_text

            first_size = first['size']
            
            # Temos um título?
            cond1 = bool(spans)

            # TODO: use condition in nested if, so that subtitles
            # are not treated as simple text
            cond3 = first_size == TITLE_SIZE
            
            not_fake = [ not re.match(_TRASH_COMPILED, sp['text']) for sp in spans]

            old_lis = hier[current_section]
            if cond1 and all(are_title_subtitle(spans)) and cond3 and all(not_fake):
                # verificar se não estende o anterior (múltiplas linhas)
                if first_size == prev_font_size and hier[current_section][-1][0][0] != 'preambulo':
                    # Multi-line titles
                    print("EXTENDING {} BY {}".format(hier[current_section][-1][0], text_block.text))
                    hier[current_section][-1][0].extend([text_block.text])
                else:                    
                    if old_lis:
                        last = old_lis[-1]
                        old_lis[-1] = ('\n'.join(last[0]), last[1])
                    old_lis.append( ([text_block.text], []) )                
            else:  # another block inside a title
                old_lis[-1][1].append(text_block)
            prev_font_size = spans[0]['size']
            prev_spans = spans.copy()
    
    aux = hier[current_section]
    aux[-1] = ('\n'.join(aux[-1][0]), aux[-1][1])
    return hier, _dbg


# In[38]:
if __name__ == '__main__':
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

    for filename in TEST_FILES[:1]:
        # try:
        h, dbg = mount_doc_hierarchy(fitz.open(filename))
        json.dump(
            [i[0] for i in h], open(str(filename)[:-4]+'.json' ,'w'),
            ensure_ascii=False, indent=4*' '
        )
        for idx, _ in enumerate(h):
            h[idx] = (_[0], [i.text for i in _[1]])
        
        json.dump(
            h, open(str(filename)[:-4]+'_secretarias.json' ,'w'),
            ensure_ascii=False, indent=4*' '
        )    
        print('\t', filename, 'OK')
        # except Exception as e:
        #     print(e)
        #     input()
        #     print('FAILED', filename)

