"""Find titles using a Filter."""

import functools


class BoldUpperCase:
    """Filter functions useful for bold and upper case text.

    Note:
        This class is static and should not be instanciated.

    """
    TEXT_MIN = 4
    TRASH_WORDS = [
        "SUMÁRIO",
        "DIÁRIO OFICIAL",
        "SEÇÃO (I|II|III)",
    ]

    BOLD_FLAGS = [16, 20]

    @classmethod
    def dict_text(cls, d):
        """Check if text is title.

        Evaluates to true if d['text'] matches the following conditions:

            - all letters are uppercase;
            - does not contain 4 or more consecutive spaces;
            - has a len greater than BoldUpperCase.TEXT_MIN/

        Returns:
            Boolean indicating if text is title.
        """
        t = d['text'].strip().strip('.')
        cond1 = 4 * " " not in t
        cond2 = len(t) > cls.TEXT_MIN
        cond3 = t == t.upper()
        return cond1 and cond2 and cond3

    @classmethod
    def dict_bold(cls, d):
        """Hmm.

        Evaluates do True if d['flags'] matches the following conditions:

            - is one of the values in BoldUpperCase.BOLD_FLAGS

        """
        flags = d['flags']
        return flags in cls.BOLD_FLAGS
