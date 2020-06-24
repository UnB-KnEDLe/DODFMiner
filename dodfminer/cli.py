"""Command Line Input handler module.

Typical usage example:
    args = CLI().parse()
"""

from argparse import ArgumentParser

class CLI(object):
    """CLI Class contains all parameters to handle arguments.

    Set Command Line Input groups and arguments.

    Attributes:
        parser (:obj:`ArgumentParser`): An ArgumentParser object.
        subparsers: Adds subparser to the parser, each one is like a
                    standalone aplication.
        def_start_date (str): Start date to download DODFS. Default start date to download 01/19.
        def_end_date (str): End date to download DODFS. Default end date to download 01/19.
        pure_text (bool): Enable extraction in pure text mode. Defaults to False.
        block (bool): Enable extraction in bloc mode. Defaults to False.
        titles_with_boxes (bool): Enable extraction in titles with boxes mode. Defaults to False.
        save_path (str): Save path of the download. Defaults to './data'.
        input_folder (str): Path where the extractor should look to files. Defaults to './data'.

    """

    def __init__(self):
        """Init CLI class with default values."""
        self.parser = ArgumentParser(prog="", usage='',
                                     description="", epilog='')
        self.subparsers = self.parser.add_subparsers(dest='subparser_name')
        self.def_start_date = '01/19'
        self.def_end_date = '01/19'
        self.save_path = './data'
        self.input_folder = './data'

    def _new_group(self, name, subparser):
        """Create new argument group.

        Args:
            name: Name of the group.
            subparser: The subparser.

        Returns:
            The argparse group created.

        """
        group = subparser.add_argument_group(name)
        return group

    def _download_parser(self):
        """Create parser for download configs."""
        download_parser = self.subparsers.add_parser("downloader")

        help_text = 'Folder to output the download DODFs'
        download_parser.add_argument('-sp', '--save_path', dest='save_path',
                                     default=self.save_path, type=str,
                                     help=help_text)


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

        group.add_argument('-i', '--input_folder', dest='input_folder',
                    default=self.input_folder, type=str,
                    help='Path to the PDFs folder')

        group.add_argument('-t', '--type-of-extraction', dest='type_of_extr',
                            default='pure-text', type=str,
                            choices=['pure-text', 'blocks', 'with-titles']) 

    def parse(self):
        """Create parser and parse the arguments.

        Returns:
            The cli arguments parsed.

        """
        self._download_parser()
        self._extract_content_parser()
        return self.parser.parse_args()