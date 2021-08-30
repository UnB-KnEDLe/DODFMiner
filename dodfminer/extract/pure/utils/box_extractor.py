"""Functions to extract boxes from text."""

import typing_extensions
import fitz

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
        List[List[tuple(float, float, float, float, str, int, int, int)]]

    """
  
    text_blocks = [page.getTextBlocks() for page in doc]
    return _identify_text_boxes(text_blocks)

def _identify_text_boxes(doc_boxes):
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

def _group_blocks_by_identifier(doc_boxes):
    remove_duplicates = lambda x: list(set(x))
    doc_blocks = []
    page_blocks = []

    for page in doc_boxes:
        get_id = lambda x: x[7]
        page_ids = remove_duplicates(list(map(get_id, page)))
        
        for id in page_ids:
            blocks_left = list(filter(lambda x: int(x[0]) < 418 and x[7] == id, page))
            blocks_right = list(filter(lambda x: int(x[0]) >= 418 and x[7] == id, page))

            if len(blocks_left): 
                page_blocks.append(_return_fused_block_if_possible(blocks_left))
            if len(blocks_right): 
                page_blocks.append(_return_fused_block_if_possible(blocks_right))
        
        doc_blocks.append(page_blocks)
        page_blocks = []
    
    return doc_blocks

def _return_fused_block_if_possible(blocks):
    if len(blocks) > 1:
        new_block = _fuse_blocks(blocks)
        return new_block
    else:
        return blocks[0]
                
def _fuse_blocks(blocks):
    texts = list(map(lambda x: x[4], blocks))
    fused_text = " ".join(texts)

    x0, y0, x1, _, _, index, block_type, id = blocks[0]
    _, _, _, y1, *_ = blocks[-1]

    fused_block = (x0, y0, x1, y1, fused_text, index, block_type, id)
    return fused_block

    
def _is_a_valid_box(x0, x1):
    in_column1_bounds = x0 >= 55 and x1 <= 405
    in_column2_bounds = x0 >= 417 and x1 <= 766

    is_inbounds = (in_column1_bounds or in_column2_bounds)
    is_column_text = (x0 >= 55 and x0 <= 57) or (x0 >= 417 and x0 <= 419)

    return is_inbounds and is_column_text

def _is_a_complete_text(text):
    return text[-1] == '.' or "\nBrasília" in text[text.rfind('.'):] or text[text.rfind('.'):].isupper()

def get_doc_text_lines(doc: fitz.Document):
    """Returns list of list of extracted text lines.

    Args:
        doc: an opened fitz document.

    Returns:
        List[List[tuple(float, float, float, str)]]

    """

    return [_extract_page_lines_content(page) for page in doc]

def draw_doc_text_boxes(doc: fitz.Document, doc_boxes):
    color = fitz.utils.getColor("greenyellow")

    for page in doc:
        for page_box in doc_boxes[page.number]:
            x0, y0, x1, y1, *_ = page_box
            rect = fitz.Rect(x0, y0, x1, y1)

            page.drawRect(rect, color, width=2)
    
    doc_path = '/'.join(doc.name.split('/')[0:-1])
    doc_name = doc.name.split('/')[-1]

    doc.save(f"{doc_path}{'/' if len(doc_path) else ''}BOXES_{doc_name}")

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
        img_ll[idx] = [page.getImageBbox(img) for img in img_lis]

    return img_ll
