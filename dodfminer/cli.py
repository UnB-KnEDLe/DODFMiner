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
        def_start_date: Default start date to download 01/19.
        def_end_date: Default end date to download 01/19.
        def_single: Download a single PDF if True.
        def_extract_content: Extract content from downloaded pdfs if True.
        update_base: Update title and subtitle database if true.

    """

    def __init__(self):
        """Init CLI class with default values."""
        self.parser = ArgumentParser(prog="", usage='',
                                     description="", epilog='')
        self.subparsers = self.parser.add_subparsers(dest='subparser_name')
        self.def_start_date = '01/19'
        self.def_end_date = '01/19'
        self.def_single = False
        self.def_extract_content = False
        self.update_base = False

        self.def_dpi = 300
        self.def_file_format = 'jpg'

        self.def_language = 'por'
        self.def_callback = None

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
        """Create group for download configs."""
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
        """Create group for extraction configs."""
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

        group.add_argument('--callback', dest='cb_type',
                           default=self.def_callback, type=str,
                           help='Callback to the extraction function')

    def _prextract_parser(self):
        """Create group for pre-extraction configs."""
        preextract_parser = self.subparsers.add_parser("prextract")

        preextract_parser.add_argument('-u', '--update_base', type=bool,
                                       dest='update_base',
                                       default=self.def_extract_content,
                                       help='Extract Titles and Subtitles')

    def parse(self):
        """Create groups and parse the arguments.

        Returns:
            The cli arguments parsed.

        """
        self._download_parser()
        self._extract_content_parser()
        self._prextract_parser()
        return self.parser.parse_args()


GLOBAL_ARGS = CLI().parse()
