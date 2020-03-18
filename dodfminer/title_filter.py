"""Missing Doc."""

import functools


class NegritoCaixaAlta:
    """Missing Summary.

    Static class to return filter functions useful
    for bold and upper case text.
    """

    TEXT_MIN = 4
    TRASH_WORDS = [
        "SUMÁRIO",
        "DIÁRIO OFICIAL",
        "SEÇÃO (I|II|III)"
    ]

    @staticmethod
    def dict_text(d):
        """Missing Summary."""
        t = d['text'].strip().strip('.')
        cond1 = 4 * " " not in t
        cond2 = len(t) > NegritoCaixaAlta.TEXT_MIN
        cond3 = t == t.upper()
        return cond1 and cond2 and cond3

    @staticmethod
    def dict_bold(d):
        """Missing Summary."""
        flags = d['flags']
        return flags in (16, 20)

    @staticmethod
    def params(params_sep_underscore):
        """Missing Summary.

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
            func_lis.append(eval("NegritoCaixaAlta.dict_{}".format(criteria)))

        def and_funcs(arg):
            return functools.reduce(lambda a, b: a and b,
                                    map(lambda fun: fun(arg), func_lis))
        return and_funcs
