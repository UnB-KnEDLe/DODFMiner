from operator import itemgetter
from itertools import groupby
import fitz

COLOR = {
    'RED': (1, 0, 0),
    'GREEN': (0, 1, 0),
    'BLUE': (0, 0, 1),
    'WHITE': (1, 1, 1),
    'BLACK': (0, 0, 0),
    'YELLOW': tuple([i/255 for i in (252, 236, 3)]),   
    'PURPLE': tuple([i/255 for i in (123, 22, 188)]),   
}

WIDTH = {
    'img': 3,
    'txt': 2,
    'word': 1,
    'line': 1,
}

def extract_page_lines(page):
    """Extracts page lines;

    Args:
        page: fitz.fitz.Page object to have its bold content extracted.

    Returns:
        A list containing lines content at the page.

    """
    lis = []
    for bl in page.getTextPage().extractDICT()['blocks']:
        for line in bl['lines']:
            for span in line['spans']:
                del span['color']
                del span['flags']
                lis.append(( *span['bbox'], span['text'] ))
                # lis.append(span)
    return lis


# https://pymupdf.readthedocs.io/en/latest/faq/#drawing-and-graphics


def _recover_words(words, rect, thresh_divisor=5):
    """ Word recovery.

    Notes:
        Method 'getTextWords()' does not try to recover words, if their single
        letters do not appear in correct lexical order. This function steps in
        here and creates a new list of recovered words.
    Args:
        words: list of words as created by 'getTextWords()'
        rect: rectangle to consider (usually the full page)
        thresh_quocient: TODO 
    Returns:
        List of recovered words. Same format as 'getTextWords', but left out
        block, line and word number - a list of items of the following format:
        [x0, y0, x1, y1, "word"]
    """
    # build my sublist of words contained in given rectangle
    mywords = [w for w in words if fitz.Rect(w[:4]) in rect]

    # sort the words by lower line, then by word start coordinate
    mywords.sort(key=itemgetter(3, 0))  # sort by y1, x0 of word rectangle

    # build word groups on same line
    grouped_lines = groupby(mywords, key=itemgetter(3))

    words_out = []  # we will return this

    # iterate through the grouped lines
    # for each line coordinate ("_"), the list of words is given
    for _, words_in_line in grouped_lines:
        for i, w in enumerate(words_in_line):
            if i == 0:  # store first word
                x0, y0, x1, y1, word = w[:5]
                continue

            r = fitz.Rect(w[:4])  # word rect

            # Compute word distance threshold as (100 / thresh_divisor)% of width of 1 letter.
            # So we should be safe joining text pieces into one word if they
            # have a distance shorter than that.
            threshold = r.width / len(w[4]) / thresh_divisor
            if r.x0 <= x1 + threshold:  # join with previous word
                word += w[4]  # add string
                x1 = r.x1  # new end-of-word coordinate
                y0 = max(y0, r.y0)  # extend word rect upper bound
                continue

            # now have a new word, output previous one
            words_out.append([x0, y0, x1, y1, word])

            # store the new word
            x0, y0, x1, y1, word = w[:5]

        # output word waiting for completion
        words_out.append([x0, y0, x1, y1, word])

    return words_out



def drawBoxes(doc, img=True, txt=True, line=True, word=False, **kargs):
    """
    Draws rectangles using the bounding boxes of images, text blocks, text lines and text words.
    Usage example:
    
    >>> p = '22012019.pdf'
    >>> d = fitz.open(p)
    >>> drawBoxes(d)
    >>> d.save(d.name.replace('.pdf', '_drawBoxes.pdf'))

    Args:
        img: wheter images bounding boxes should be marked
        txt: wheter text blocks bounding boxes should be marked
        line: wheter text lines bounding boxes should be marked
        word: wheter words bounding boxes should be marked
        kargs: keys in ['color_img', 'width_img', 'color_txt', 'width_txt',
                'color_word', 'width_word', 'color_line', 'width_line'] are used. In absence of them,
                default values are used. They are repectively:
                [COLOR['GREEN'], 3, COLOR['BLACK'], 2, COLOR['YELLOW', 1, COLOR['RED'], 1]
    Returns:
        The `doc` with the drawn rects. `doc` is modified  (marked) inplace.

    """

    color_img = kargs.get('color_img', COLOR['GREEN'])
    color_txt = kargs.get('color_txt', COLOR['BLACK'])
    color_word = kargs.get('color_word', COLOR['YELLOW'])
    color_line = kargs.get('color_line', COLOR['RED'])

    width_img = kargs.get('width_img', WIDTH['img'])
    width_txt = kargs.get('width_txt', WIDTH['txt'])
    width_word = kargs.get('width_word', WIDTH['word'])
    width_line = kargs.get('width_line', WIDTH['line'])

    for page in doc:
        if img:
        	for img in page.getImageList(full=True):
        		page.drawRect(page.getImageBbox(img), color=color_img, width=width_img)
        if txt:
        	for textBlock in page.getTextBlocks():
        		page.drawRect(textBlock[:4], color=color_txt, width=width_txt)
        if line:
        	for line in extract_page_lines(page):
        		page.drawRect(line[:4], color=color_line, width=width_line)
        if word:
        	for word in _recover_words(page.getTextWords(), page.rect):
        		page.drawRect(word[:4], color=color_word, width=width_word)
    return doc


