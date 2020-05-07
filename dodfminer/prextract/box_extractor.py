import fitz
from typing import List

def _extract_page_lines_content(page):
	"""Extracts page lines;

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
				lis.append(( *span['bbox'], span['text'] ))
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
	"""Returns list of list of extracted text lines.

	Args:
		doc: an opened fitz document

	Returns:
		List[List[tuple(float, float, float, str)]]
	"""

	return [_extract_page_lines_content(page) for page in doc]


def _get_doc_img(doc: fitz.Document):
	"""Returns list of list of image items.
	
	ObS: this function is not intented to be used by final users,
		but internally. Image `items` are described at:

		https://pymupdf.readthedocs.io/en/latest/page/#Page.getImageBbox

	Args:
		doc: an opened fitz document

	Returns:
		List[List[tuple(int, int, int, int, str, str, str, str, int)]]
		(xref, smask, width, height, bpc, colorspace, alt. colorspace, filter, invoker)
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
		img_ll[idx] = [ page.getImageBbox(img) for img in  img_lis]

	return img_ll

