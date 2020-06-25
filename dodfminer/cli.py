"""Command Line Input handler module.

Typical usage example:
    args = CLI().parse()
"""

from argparse import ArgumentParser

class CLI(object):
    """CLI Class contains all parameters to handle arguments.

    Set Command Line Input groups and arguments.

    Attributes:
        parser: An ArgumentParser object.
        subparsers: Adds subparser to the parser, each one is like a
                    standalone aplication.
        def_start_date: Default start date to download 01/19.
        def_end_date: Default end date to download 01/19.
        def_single: Download a single PDF if True.
        update_base: Update title and subtitle database if true.
        def_dpi: Default dpi for the pdf2image.
        def_file_format: Default file format output for pdf2image.
        def_language:  Default language for tesseract
        def_callback: Default callback to the extraction process
    """

    def __init__(self):
        """Init CLI class with default values."""
        self.parser = ArgumentParser(prog="", usage='',
                                     description="", epilog='')
        self.subparsers = self.parser.add_subparsers(dest='subparser_name')
        self.def_start_date = '01/19'
        self.def_end_date = '01/19'
        self.def_single = False
        self.update_base = False
        self.def_dpi = 300
        self.def_file_format = 'jpg'
        self.def_language = 'por'
        self.def_callback = []
        self.backend = 'tesseract'
        self.pure_text = False
        self.titles_with_boxes = False

    def _new_group(self, name, subparser):
        """Create new argument group.

        Args:
            name: Name of the group.

        Returns:
            The argparse group created.

        """
        group = subparser.add_argument_group(name)
        return group

    def _download_parser(self):
        """Create parser for download configs."""
        download_parser = self.subparsers.add_parser("fetch")

        download_parser.add_argument('-s', '--single', dest='single',
                                     default=self.def_single, type=bool,
                                     help='Download a single DODF pdf file.')

        help_text = 'Input the date in either mm/yy or mm-yy.'
        download_parser.add_argument('-sd', '--start_date', dest='start_date',
                                     default=self.def_start_date, type=str,
                                     help=help_text)

        help_text = 'Input the date in either mm/yy or mm-yy.'
        download_parser.add_argument('-ed', '--end_date', dest='end_date',
                                     default=self.def_end_date, type=str,
                                     help=help_text)

    def _extract_content_parser(self):
        """Create parser for extraction configs."""
        download_parser = self.subparsers.add_parser("extract")

        group = self._new_group('PDF2Image Configs', download_parser)

        group.add_argument('-dpi', dest='dpi', default=self.def_dpi, type=int,
                           help='The DPI to transform the pdf to image')

        group.add_argument('-fmt', '--file_format', dest='file_format',
                           default=self.def_file_format, type=str,
                           help='The output format of the image created')

        group = self._new_group('Tesseract Configs', download_parser)

        group.add_argument('-lang', '--language', dest='tesseract_lang',
                           default=self.def_language, type=str,
                           help='Tesseract Default Language')

        group.add_argument('-be', '--backend', dest='backend',
                           default=self.backend, type=str,
                           help='Backend for extraction (tesseract/drawboxes)')

        group.add_argument('-p', '--pure', dest='pure_text',
                           default=self.pure_text, type=bool,
                           help='Extract pure text in txt format')
        
        group.add_argument('-tb', '--titles-with-boxes', dest='titles_with_boxes',
                           default=self.titles_with_boxes, type=bool,
                           help='Extract titles and your text boxes from dodf')

        group.add_argument('--callback', dest='cb_type',
                           default=self.def_callback, type=str,
                           choices=['spellcheck', 'None'],
                           help='Callback to the extraction function')

    def _prextract_parser(self):
        """Create parser for pre-extraction configs."""
        _ = self.subparsers.add_parser("prextract")

    def parse(self):
        """Create parser and parse the arguments.

        Returns:
            The cli arguments parsed.

        """
        self._download_parser()
        self._extract_content_parser()
        self._prextract_parser()
        return self.parser.parse_args()


GLOBAL_ARGS = CLI().parse()
