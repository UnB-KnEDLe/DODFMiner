import functools

class NegritoCaixaAlta:
    """
    Static class to return filter functions useful for bold and upper case text.
    """
    TEXT_MIN = 4
    TRASH_WORDS = [
        "SUMÁRIO",
        "DIÁRIO OFICIAL",
        "SEÇÃO (I|II|III)"
    ]

    @staticmethod
    def dict_text(d: dict):
        t = d['text'].strip().strip('.')
        return 4 * " " not in t and len(t) > NegritoCaixaAlta.TEXT_MIN and t == t.upper()

    @staticmethod
    def dict_bold(d: dict):
        flags:int = d['flags']
        return flags in (16, 20)

    @staticmethod
    def params(params_sep_underscore :str):
        """
        params_sep_underscore must be a compound string
        wich will be splited based on '_'. Each os these strings
        specify a different filter.
        Ex:
          params("font_text") returns something like:
            def gambs(x):
              return dict_font(x) and dict_text(x)
        """
        func_lis :list = []
        for criteria in params_sep_underscore.split('_'):
            func_lis.append( eval("NegritoCaixaAlta.dict_{}".format(criteria)) )

        def and_funcs(arg):
            return functools.reduce(lambda a,b: a and b, map(lambda fun: fun(arg), func_lis))
        return and_funcs
