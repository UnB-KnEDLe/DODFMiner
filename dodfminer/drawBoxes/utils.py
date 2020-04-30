from collections import namedtuple

RGB = namedtuple("RGB", "R G B")

class MetaDataClass(type):
	"""
	This class is expected to be inherited and used as a metaclass
	at the same time.

	Is provides an access to _colors values through index-syntax.
	The class is intended to be read-only and only return 3-uples
	(RGB) Which conatains numbers in range [0, 1].

	Methods:
		values: returns copy of dict '_values' -> RGB
		items: returns list with `_values` values
		keys: returns list with `values` keys
	"""

	_values={}
	
	@classmethod
	def items(cls):
		return list(cls._values.items())


	@classmethod
	def values(cls):
		return cls._values.copy()

	@classmethod
	def keys(cls):
		return list(cls._values.keys())


	def __getitem__(self, color):
		"""Returns RGB tuple corresponding to color.

		Args:
			color: string to be used as key of self.values
		Returns:
			RGB tuple if color in self.values. None otherwise
		"""
		return self._values.get(color)


	def __setitem__(self, color, val):
		raise TypeError("{} types does not support item assignment.".format(type(self)))


class Dogs(MetaDataClass, metaclass=MetaDataClass):

	# Just for testing.
	_values = {
		'dog': 'kelly',
		'cat': 'garfield',
	}
