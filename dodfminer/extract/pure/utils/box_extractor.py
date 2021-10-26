"""Functions to extract boxes from text."""

import fitz
import re
from functools import cmp_to_key, reduce
import operator

SECTION_TITLES = ["SEÇÃO I", "SEÇÃO II", "SEÇÃO III"]


def _extract_page_lines_content(page):
    """Extracts page lines.

    Args:
        page: fitz.fitz.Page object to have its bold content extracted.

    Returns:
        List[tuple(float, float, float, float, str)]
        A list containing lines content at the page, along with
        its bounding boxes.

    """
    lis = []
    for bl in page.getTextPage().extractDICT()['blocks']:
        for line in bl['lines']:
            for span in line['spans']:
                del span['color']
                del span['flags']
                lis.append((*span['bbox'], span['text']))
    return lis


def get_doc_text_boxes(doc: fitz.Document):
    """Returns list of list of extracted text blocks.

    Args:
        doc: an opened fitz document.

    Returns:
        List[List[tuple(float, float, float, float, str, int, int)]]

    """

    text_blocks = [sort_blocks(clean_section_boxes(page)) for page in doc]
    return text_blocks


def sort_blocks(page_blocks):
    """Sort blocks by their vertical and horizontal position.

        Args:
            page_blocks: a list of blocks within a page.

        Returns:
            List[tuple(float, float, float, float, str, int, int)]
    """
    return sorted(page_blocks, key=cmp_to_key(compare_blocks))


def compare_blocks(block1, block2):
    """Implements a comparison heuristic between blocks.
       Blocks that are in the uppermost and leftmost positions 
       should be inserted before the other block in comparison.

    Args:
        block1: a block tuple to be compared.
        block2: a block tuple to be compared to.

    Returns:
        Int
    """
    b1_x0, b1_y0, b1_x1, b1_y1, *_ = block1
    b2_x0, b2_y0, b2_x1, b2_y1, *_ = block2

    b1_y = max([b1_y0, b1_y1])
    b2_y = max([b2_y0, b2_y1])

    if (b1_x0 >= 55 and b1_x1 <= 405 and b2_x0 >= 55 and b2_x1 <= 405) or \
       (b1_x0 >= 417 and b1_x1 <= 766 and b2_x0 >= 417 and b2_x1 <= 766) or \
       (b1_x1-b1_x0 > 350) or \
       (b2_x1-b2_x0 > 350) or \
       (b1_y < 80) or \
       (b2_y < 80):
        return b1_y-b2_y
    else:
        return b1_x0-b2_x0


def clean_section_boxes(page):
    blocks = page.getTextBlocks()

    section_blocks = list(filter(lambda x: re.match("SEÇÃO (I|II|III)", x[4]), blocks))

    if section_blocks:
        separated_section_blocks = map(
            lambda x: separate_section_blocks(page, x), section_blocks)
        joined_section_blocks = reduce(operator.add, separated_section_blocks)
        section_blocks = list(filter(None, joined_section_blocks))

    not_section_blocks = list(filter(lambda x: not re.match("SEÇÃO (I|II|III)", x[4]), blocks))

    return not_section_blocks + section_blocks


def separate_section_blocks(page, box):
    rect = fitz.Rect(box[:4])

    def extract_box(x): return x['bbox'] + (x['text'], box[5], box[6])

    section_box = []
    rest_box = []

    box_dict = page.getText('dict', clip=rect)['blocks'][0]['lines']

    for span_dict in box_dict:
        span_list = span_dict['spans']
        boxes = list(map(extract_box, span_list))

        section_box = section_box + \
            list(filter(lambda x: x[4] in SECTION_TITLES, boxes))
        rest_box = rest_box + \
            list(filter(lambda x: not x[4] in SECTION_TITLES, boxes))

    return [_fuse_blocks(rest_box) if rest_box else (), section_box[0]]


def identify_text_boxes(doc_boxes):
    """Insert id component into block tuple for block aggrupation.

    Args:
        doc_boxes: the list of blocks on a document, separated by pages.

    Returns:
        List[List[tuple(float, float, float, float, str, int, int, int)]]
    """
    id = 0
    incomplete_block = None
    doc_blocks = []
    page_blocks = []

    for page in doc_boxes:
        for box in page:
            x0, _, x1, _, text, *_ = box

            if incomplete_block != None and _is_a_valid_box(x0, x1):
                box = box + (incomplete_block[7],)
                incomplete_block = None

            else:
                box = box + (id,)
                id += 1

            if not _is_a_complete_text(text) and _is_a_valid_box(x0, x1):
                incomplete_block = box

            page_blocks.append(box)

        doc_blocks.append(page_blocks)
        page_blocks = []

    return doc_blocks


def group_blocks_by_identifier(doc_boxes):
    """Group blocks in a same page by a id component

    Args:
        doc_boxes: the list of blocks on a document, separated by pages.

    Returns:
        List[List[tuple(float, float, float, float, str, int, int, int)]]
    """
    def remove_duplicates(x): return list(set(x))
    doc_blocks = []
    page_blocks = []

    for page in doc_boxes:
        def get_id(x): return x[7]
        page_ids = remove_duplicates(list(map(get_id, page)))

        for id in page_ids:
            blocks_left = list(
                filter(lambda x: int(x[0]) < 418 and x[7] == id, page))
            blocks_right = list(
                filter(lambda x: int(x[0]) >= 418 and x[7] == id, page))

            if len(blocks_left):
                page_blocks.append(
                    _return_fused_block_if_possible(blocks_left))
            if len(blocks_right):
                page_blocks.append(
                    _return_fused_block_if_possible(blocks_right))

        doc_blocks.append(page_blocks)
        page_blocks = []

    return doc_blocks


def draw_doc_text_boxes(doc: fitz.Document, doc_boxes, save_path=None):
    """Draw extracted text blocks rectangles.
       In result, a pdf file with rectangles shapes added, representing the extracted blocks,
       is saved.

    Args:
        doc: an opened fitz document
        doc_boxes: the list of blocks on a document, separated by pages
        save_path: a custom path for saving the result pdf 

    Returns:
        None
    """
    color = fitz.utils.getColor("greenyellow")

    for page in doc:
        for page_box in doc_boxes[page.number]:
            x0, y0, x1, y1, *_ = page_box
            rect = fitz.Rect(x0, y0, x1, y1)

            page.drawRect(rect, color, width=2)

    doc_path = '/'.join(doc.name.split('/')[0:-1])
    doc_name = doc.name.split('/')[-1]

    if save_path != None:
        doc.save(f"{save_path}/BOXES_{doc_name}")
    else:
        doc.save(f"{doc_path}{'/' if len(doc_path) else ''}BOXES_{doc_name}")


def _return_fused_block_if_possible(blocks):
    """Fuse a list of blocks if necessary

    Args:
        blocks: a list of blocks to be fused.

    Returns:
        List[List[tuple(float, float, float, float, str, int, int, int)]]
    """
    if len(blocks) > 1:
        new_block = _fuse_blocks(blocks)
        return new_block
    else:
        return blocks[0]


def _fuse_blocks(blocks):
    """Transform a list of block into one fused block.
       The block coordinates and text are changed to represent the
       multiple blocks as a single one.

    Args:
        blocks: a list of blocks to be fused.

    Returns:
        List[List[tuple(float, float, float, float, str, int, int, int)]]
    """
    texts = list(map(lambda x: x[4], blocks))
    fused_text = " ".join(texts)

    x0_1, y0, x1_1, *_ = blocks[0]
    x0_2, _, x1_2, y1, *_ = blocks[-1]

    x0 = min([x0_1, x0_2])
    x1 = max([x1_1, x1_2])

    fused_block = (x0, y0, x1, y1, fused_text) + blocks[0][5:]
    return fused_block


def _is_a_valid_box(x0, x1):
    """Determines conditions for id sharing in the identifying 
       process of blocks

    Args:
        x0: x0 coordinate of a block.
        x1: x1 coordinate of a block.

    Returns:
        bool
    """
    in_column1_bounds = x0 >= 55 and x1 <= 405
    in_column2_bounds = x0 >= 417 and x1 <= 766

    is_inbounds = (in_column1_bounds or in_column2_bounds)
    is_column_text = (x0 >= 55 and x0 <= 57) or (x0 >= 417 and x0 <= 419)

    return is_inbounds and is_column_text


def _is_a_complete_text(text):
    """Heuristic to determine if a text contains a complete information.

    Args:
        text: a string.

    Returns:
        bool
    """
    rest_of_text = text[text.rfind('.')+1:]
    supposed_author = rest_of_text.strip().split(
        '\n')[0] if '\n' in rest_of_text else ""
    last_char = text[-1]
    is_summary_text = "...." in text

    supposed_author_dotless = re.search("(\n[A-Z-ÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ. ]+$)", text)
    supposed_author_dotless = supposed_author_dotless.group(
        0) if supposed_author_dotless else ""

    return is_summary_text or last_char == '.' or "\nBrasília" in rest_of_text or supposed_author.isupper() or supposed_author_dotless.isupper()


def get_doc_text_lines(doc: fitz.Document):
    """Returns list of list of extracted text lines.

    Args:
        doc: an opened fitz document.

    Returns:
        List[List[tuple(float, float, float, str)]]

    """

    return [_extract_page_lines_content(page) for page in doc]


def _get_doc_img(doc: fitz.Document):
    """Returns list of list of image items.

    Note:
        This function is not intented to be used by final users,
        but internally. Image `items` are described at:

        https://pymupdf.readthedocs.io/en/latest/page/#Page.getImageBbox

    Args:
        doc: an opened fitz document

    Returns:
        List[List[tuple(int, int, int, int, str, str, str, str, int)]]
        (xref, smask, width, height, bpc, colorspace,
         alt. colorspace, filter, invoker)
    """

    return [page.getImageList(full=True) for page in doc]


def get_doc_img_boxes(doc: fitz.Document):
    """Returns list of list of bouding boxes of extracted images.

    Args:
        doc: an opened fitz document

    Returns:
        List[List[Rect(float, float, float, float)]]. Each Rect represents
            an image bounding box.

    """

    img_ll = _get_doc_img(doc)
    for idx, img_lis in enumerate(img_ll):
        page = doc[idx]
        img_list_altered = []

        for img in img_lis:
            img = img[:9] + (0,)
            img_list_altered.append(img)

        img_ll[idx] = [page.getImageBbox(img) for img in img_list_altered]

    return img_ll
