import fitz

def _extract_page_lines(page):
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



def get_doc_text_boxes(doc: fitz.Document):
    """Returns list of list of extracted text blocks.

    Args:
        doc: an opened fitz document

    Returns:
        List[List[tuple(float, float, float, float, str, int, int)]]
    """

    return [page.getTextBlocks() for page in doc]


def get_doc_text_lines(doc: fitz.Document):
    """Returns list o list of extracted text lines.

    Args:
        doc: an opened fitz document

    Returns:
        List[List[tuple(float, float, float, float, str, int, int)]]
    """

    return [_extract_page_lines(page) for page in doc]


def get_doc_img_boxes(doc: fitz.Document):
    """Returns list o list of extracted image blocks.

    Args:
        doc: an opened fitz document

    Returns:
        List[List[tuple(float, float, float, float, str, int, int)]]
    """

    return [page.getImageList(full=True) for page in doc]
