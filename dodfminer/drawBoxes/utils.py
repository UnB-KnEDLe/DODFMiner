from collections import namedtuple

class MetaDataClass(type):
	"""Adds dict-like behavior to the class while avoi

	This class is expected to be inherited and used as a metaclass
	at the same time.

	It provides access to `_values` values through index-syntax.
	The class is intended to be read-only. `_values` is expected
	to remain constant (the user is not expected to modify it).

	Usage example: please check `drawBoxes.py` and look at class 
		`LINE_WITDH` or `ELEMENT_COLOR`. These are examples oh how
		to use that class.

	Methods:
		values: returns copy of dict '_values'
		items: returns list with `_values` values
		keys: returns list with `values` keys
	"""

	_values={}
	
	@classmethod
	def items(cls):
		"""Gets class internal items.

		Returns:
			Returns iterable with keys and values present in the class,
			just like `dict.items`.
		"""
		return cls._values.items()

	@classmethod
	def values(cls):
		"""Gets class internal values.

		Returns:
			values inside `_values`, just like `dict.value`

		"""
		return cls._values.copy()

	@classmethod
	def keys(cls):
		"""Gets class internal keys.

		Returns:
			keys of `_values`, just like `dict.keys`

		"""
		return list(cls._values.keys())

	def __getitem__(self, key):
		"""Returns value mapped by `key`.

		Args:
			color: string to be used as key of self.values
		Returns:
			Content of _values[key] if key is present. `None` otherwise
		"""
		return self._values.get(key)
		
	def __setitem__(self, key, val):
		raise TypeError("{} types does not support item assignment.".format(type(self)))


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
	return lis


