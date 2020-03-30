"""Missing Doc."""

import functools


class BoldUpperCase:
    """
    Static class to return filter functions useful
    for bold and upper case text.
    """

    TEXT_MIN = 4
    TRASH_WORDS = [
        "SUMÁRIO",
        "DIÁRIO OFICIAL",
        "SEÇÃO (I|II|III)",
    ]

    BOLD_FLAGS = [16, 20]

    @staticmethod
    def dict_text(d):
        """Evaluates to true if d['text'] matches the following conditions:
            - all letters are uppercase
            - does not contain 4 or more consecutive spaces
            - has a len greater than BoldUpperCase.TEXT_MIN
        ."""
        t = d['text'].strip().strip('.')
        cond1 = 4 * " " not in t
        cond2 = len(t) > BoldUpperCase.TEXT_MIN
        cond3 = t == t.upper()
        return cond1 and cond2 and cond3

    @staticmethod
    def dict_bold(d):
        """Evaluates do True if d['flags'] matches the following conditions:
            - is one of the values in BoldUpperCase.BOLD_FLAGS
        ."""
        flags = d['flags']
        return flags in BoldUpperCase.BOLD_FLAGS

    @staticmethod
    def params(params_sep_underscore):
        """Returns an function which evaluates a conjunction over the results
        of all filters specified by params_sep_underscore.

        params_sep_underscore must be a compound string
        wich will be splited based on '_'. Each os these strings
        specify a different filter.
        Ex:
          params("font_text") returns something like:
            def gambs(x):
              return dict_font(x) and dict_text(x)
        """
        func_lis: list = []
        for criteria in params_sep_underscore.split('_'):
            func_lis.append(eval("BoldUpperCase.dict_{}".format(criteria)))

        def and_funcs(arg):
            return functools.reduce(lambda a, b: a and b,
                                    map(lambda fun: fun(arg), func_lis))
        return and_funcs
