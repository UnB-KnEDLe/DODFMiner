"""Find titles using a Filter."""


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
    def dict_text(cls, data):
        """Check if text is title.

        Evaluates to true if d['text'] matches the following conditions:

            - all letters are uppercase;
            - does not contain 4 or more consecutive spaces;
            - has a len greater than BoldUpperCase.TEXT_MIN/

        Returns:
            Boolean indicating if text is title.
        """
        text = data['text'].strip().strip('.')
        cond1 = 4 * " " not in text
        cond2 = len(text) > cls.TEXT_MIN
        cond3 = text == text.upper()
        return cond1 and cond2 and cond3

    @classmethod
    def dict_bold(cls, data):
        """Hmm.

        Evaluates do True if d['flags'] matches the following conditions:

            - is one of the values in BoldUpperCase.BOLD_FLAGS

        """
        flags = data['flags']
        return flags in cls.BOLD_FLAGS
