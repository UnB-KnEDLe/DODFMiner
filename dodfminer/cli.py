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
        self.def_start_date = '01/19'
        self.def_end_date = '01/19'
        self.def_single = False
        self.def_extract_content = False
        self.update_base = False

    def _new_group(self, name):
        """Create new argument group.

        Args:
            name: Name of the group.

        Returns:
            The argparse group created.

        """
        group = self.parser.add_argument_group(name)
        return group

    def _download_group(self):
        """Create group for download configs."""
        group = self._new_group('Download Configs')

        group.add_argument('-s', '--single', dest='single',
                           default=self.def_single, type=bool,
                           help='Download a single DODF pdf file.')

        group.add_argument('-sd', '--start_date', dest='start_date',
                           default=self.def_start_date, type=str,
                           help='Input the date in either mm/yy or mm-yy.')

        group.add_argument('-ed', '--end_date', dest='end_date',
                           default=self.def_end_date, type=str,
                           help='Input the date in either mm/yy or mm-yy.')

    def _extract_content_group(self):
        """Create group for extraction configs."""
        group = self._new_group('Extract Configs')

        group.add_argument('-ext', '--extract_content', dest='extract_content',
                           default=self.def_extract_content, type=bool,
                           help='Extract contents to json')

    def _prextract_group(self):
        """Create group for pre-extraction configs."""
        group = self._new_group('Prextract Configs')

        group.add_argument('-u', '--update_base', dest='update_base',
                           default=self.def_extract_content, type=bool,
                           help='Extract Titles and Subtitles to JSON')

        return group

    def parse(self):
        """Create groups and parse the arguments.

        Returns:
            The cli arguments parsed.

        """
        self._download_group()
        self._extract_content_group()
        self._prextract_group()
        return self.parser.parse_args()
