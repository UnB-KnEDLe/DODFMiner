"""Command Line Input handler module.

Typical usage example:
    args = CLI().parse()
"""

from dodfminer.__version__ import __version__
from argparse import ArgumentParser

act_choices = ["aposentadoria",
                "reversoes",
                "nomeacao",
                "exoneracao",
                "abono",
                "retificacoes",
                "substituicao",
                "cessoes",
                "sem_efeito_aposentadoria",
                "efetivos_nome",
                "efetivos_exo"]

class CLI(object):
    """CLI Class contains all parameters to handle arguments.

    Set Command Line Input groups and arguments.

    Attributes:
        parser (:obj:`ArgumentParser`): An ArgumentParser object.
        subparsers: Adds subparser to the parser, each one is like a
                    standalone aplication.
        def_start_date (str): Start date to download DODFS. Default start date
                              to download 01/19.
        def_end_date (str): End date to download DODFS. Default end date
                            to download 01/19.
        pure_text (bool): Enable extraction in pure text mode.
                          Defaults to False.
        block (bool): Enable extraction in bloc mode.
                      Defaults to False.
        titles_with_boxes (bool): Enable extraction in titles with boxes mode.
                                  Defaults to False.
        save_path (str): Save path of the download. Defaults to './data'.
        input_folder (str): Path where the extractor should look to files.
                            Defaults to './data'.

    """

    def __init__(self):
        """Init CLI class with default values."""
        desc = """Data extractor of PDF documents from the Official Gazette
                  of the Federal District, Brazil."""
        epilog = f'© Copyright 2020, KnEDLe Team. Version {__version__}'
        self.parser = ArgumentParser(prog="DODFMiner", description=desc,
                                     epilog=epilog)
        self.subparsers = self.parser.add_subparsers(dest='subparser_name')
        self.def_start_date = '01/19'
        self.def_end_date = '01/19'
        self.save_path = './'

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
        self.download_parser = self.subparsers.add_parser("downloader")

        help_text = 'Folder to output the download DODFs'
        self.download_parser.add_argument('-sp', '--save_path', dest='save_path',
                                     default=self.save_path, type=str,
                                     help=help_text)

        help_text = 'Input the date in either mm/yyyy or mm-yyyy.'
        self.download_parser.add_argument('-sd', '--start_date', dest='start_date',
                                     default=self.def_start_date, type=str,
                                     help=help_text)

        help_text = 'Input the date in either mm/yyyy or mm-yyyy.'
        self.download_parser.add_argument('-ed', '--end_date', dest='end_date',
                                     default=self.def_end_date, type=str,
                                     help=help_text)

    def _extract_content_parser(self):
        """Create parser for extraction configs."""
        self.extract_content_parser = self.subparsers.add_parser("extract")

        group = self._new_group('Extraction Configs', self.extract_content_parser)

        group.add_argument('-i', '--input-folder', dest='input_folder',
                           default='./', type=str,
                           help='Path to the PDFs folder')

        group.add_argument('-s', '--single-file', dest='single_file', type=str,
                           default=None,
                           help='Path to the single file to extract')

        group.add_argument('-t', '--type-of-extraction', dest='type_of_extr',
                           default=None, type=str, nargs='?',
                           choices=['pure-text', 'blocks', 'with-titles'],
                           help="Type of text extraction")

        group.add_argument('-a', '--act', dest='act', default='all', type=str,
                           choices=act_choices, nargs='*',
                           help='Which acts to extract to CSV')

        group.add_argument('-b', '--backend', dest='backend', default='regex',
                           type=str, choices=['regex', 'ner'],
                           help="The backend to be used in CSV extraction")

        group.add_argument('-x', '--xml', dest='xml', default=False, nargs='*',
                            type=bool, help="Generate TeamTat XML Annotations")

    def parse(self):
        """Create parser and parse the arguments.

        Returns:
            The cli arguments parsed.

        """
        self._download_parser()
        self._extract_content_parser()
        return self.parser.parse_args()
