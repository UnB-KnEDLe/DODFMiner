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
        self.pure_text = False
        self.block = False
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

        group = self._new_group('Tesseract Configs', download_parser)

        group.add_argument('-b', '--block', dest='block',
                           default=self.block, type=bool,
                           help='Extract pure text in blocks of text')

        group.add_argument('-p', '--pure-text', dest='pure_text',
                          default=self.pure_text, type=bool,
                          help='Extract pure text in txt format')
        
        group.add_argument('-tb', '--titles-with-boxes', dest='titles_with_boxes',
                           default=self.titles_with_boxes, type=bool,
                           help='Extract text separated by titles')

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
