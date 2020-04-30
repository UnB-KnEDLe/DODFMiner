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
	blocks_by_page = []
	for page in doc:
		blocks_by_page.append( page.getTextBlocks() )
	return blocks_by_page

def get_doc_text_lines(doc: fitz.Document):
	"""Returns list o list of extracted text lines.

	Args:
		doc: an opened fitz document

	Returns:
		List[List[tuple(float, float, float, float, str, int, int)]]
	"""
	lines_by_page = []
	for page in doc:
		lines_by_page.append( _extract_page_lines(page) )
	return lines_by_page

def get_doc_img_boxes(doc: fitz.Document):
	"""Returns list o list of extracted image blocks.

	Args:
		doc: an opened fitz document

	Returns:
		List[List[tuple(float, float, float, float, str, int, int)]]
	"""
	img_boxes_by_page = []
	for page in doc:
		img_boxes_by_page.append( page.getImageList(full=True) )
	return img_boxes_by_page
