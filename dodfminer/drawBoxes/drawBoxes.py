from operator import itemgetter
from itertools import groupby

import fitz


from drawBoxes.utils import MetaDataClass, extract_page_lines
from fitz.utils import getColor, getColorList


class LINE_WIDTH(MetaDataClass, metaclass=MetaDataClass):
	_values = {
		'img': 3,
		'txt': 2,
		'word': 1,
		'line': 1,
	}

class ELEMENT_COLOR(MetaDataClass, metaclass=MetaDataClass):
	_values = {
		'img': getColor('GREEN'),
		'txt': getColor('BLACK'),
		'word': getColor('YELLOW'),
		'line': getColor('RED'),
	}




# # https://pymupdf.readthedocs.io/en/latest/faq/#drawing-and-graphics
def _recover_words(words, rect, thresh_divisor=5):
	""" Word recovery.

	Notes:
		Method 'getTextWords()' does not try to recover words, if their single
		letters do not appear in correct lexical order. This function steps in
		here and creates a new list of recoveRED words.
	Args:
		words: list of words as created by 'getTextWords()'
		rect: rectangle to consider (usually the full page)
		thresh_quocient: TODO 
	Returns:
		List of recoveRED words. Same format as 'getTextWords', but left out
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


def draw(doc, img=True, txt=True, line=True, word=False, color_schema={}, width_schema={}):
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
		color_width_schema: keys in ['color_img', 'width_img', 'color_txt', 'width_txt',
				'color_word', 'width_word', 'color_line', 'width_line'] are used. In absence of them,
				default values are used. They are repectively:
				[_BOX_COLOR_MAP['GREEN'], 3, LINE_WIDTH['GREEN'],
				_BOX_COLOR_MAP['BLACK'], 2, LINE_WIDTH['BLACK'],
				_BOX_COLOR_MAP['YELLOW', 1, LINE_WIDTH['YELLOW'],
				_BOX_COLOR_MAP['RED'], 1] LINE_WIDTH['RED'],
	Returns:
		The `doc` with the drawn rects. `doc` is modified  (marked) inplace.
	
	"""


	color_img = color_schema.get('img', ELEMENT_COLOR['img'])
	color_txt = color_schema.get('txt', ELEMENT_COLOR['txt'])
	color_word = color_schema.get('word', ELEMENT_COLOR['word'])
	color_line = color_schema.get('line', ELEMENT_COLOR['line'])

	width_img = width_schema.get('img', LINE_WIDTH['img'])
	width_txt = width_schema.get('txt', LINE_WIDTH['txt'])
	width_word = width_schema.get('word', LINE_WIDTH['word'])
	width_line = width_schema.get('line', LINE_WIDTH['line'])

	# `if`s are  to implement the flag control wheter to draw or not text block, words,
	# images or lines bounding boxes.
	for page in doc:
		if img:
			for img in page.getImageList(full=True):
				page.drawRect(page.getImageBbox(img), color=color_img, width=width_img)
		if txt:
			# Iterating over blocks of text of a page. It is represented by a 7-uple
			# which first 4 elements are the bounding boxes limit (x0, y0, x1, y1).
			for textBlock in page.getTextBlocks():
				page.drawRect(textBlock[:4], color=color_txt, width=width_txt)
		if line:
			for line in extract_page_lines(page):
				page.drawRect(line[:4], color=color_line, width=width_line)
		if word:
			for word in _recover_words(page.getTextWords(), page.rect):
				page.drawRect(word[:4], color=color_word, width=width_word)
	return doc


class DrawBoxes:

	_COLOR_MAP = dict(ELEMENT_COLOR.items())

	_WIDTH_MAP = dict(LINE_WIDTH.items())

	def __init__(self, path, color_schema={}, width_schema={}):
		self._path = path
		self._fp = fitz.open(path)
		
		if not isinstance(color_schema, dict):
			raise TypeError("'color_schema' should be an dict instance.")
		
		self._color_schema = self._COLOR_MAP.copy()
		self._color_schema.update(color_schema)

		self._width_schema = self._WIDTH_MAP.copy()
		self._width_schema.update(width_schema)	
		self._color_schema = {k: tuple(v) for (k,v) in self._color_schema.items()}


	def draw(self, inplace=True, img=True, txt=True, line=True, word=False,
			color_schema={}, width_schema={}):
		"""Wraps `draw` function passing instance parameters if None is provided.

		Args:
			inplace: wheter to modify instance document
			or to create a copy and draw on it

			img: check `draw` documentation
			txt: check `draw` documentation
			line: check `draw` documentation
			word: check `draw` documentation
			color_schema: dict mapping string to 3-uples whose each
						elements must be in range [0, 1]
			width_schema: dict mapping string to integers
		
		Returns:
			the annotated document.
		
		"""
		if color_schema: self._color_schema.update(color_schema)
		if width_schema: self._color_schema.update(width_schema)
		return draw(self._fp if inplace else fitz.open(self._fp.name),
			img=img, txt=txt, line=line, word=word,
			color_schema=self._color_schema, width_schema=self._width_schema)

	def save(self, path):
		self._fp.save(path)


