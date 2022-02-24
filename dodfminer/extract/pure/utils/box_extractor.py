"""Functions to extract boxes from text."""

import fitz

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
    for block in page.get_textpage().extractDICT()['blocks']:
        for line in block['lines']:
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

    text_blocks = [ page.get_text('blocks', flags=0) for page in doc ]
    return text_blocks


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
            x_0, y_0, x_1, y_1, *_ = page_box
            rect = fitz.Rect(x_0, y_0, x_1, y_1)

            page.drawRect(rect, color, width=2)

    doc_path = '/'.join(doc.name.split('/')[0:-1])
    doc_name = doc.name.split('/')[-1]

    if save_path is not None:
        doc.save(f"{save_path}/BOXES_{doc_name}")
    else:
        doc.save(f"{doc_path}{'/' if doc_path else ''}BOXES_{doc_name}")


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

    return [page.get_images(full=True) for page in doc]


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

        img_ll[idx] = [page.get_image_bbox(img) for img in img_list_altered]

    return img_ll
