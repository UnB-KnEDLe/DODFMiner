"""."""

from argparse import ArgumentParser


class CLI(object):
    """."""

    def __init__(self):
        """Eita."""
        self.parser = ArgumentParser(prog="", usage='',
                                     description="", epilog='')
        self.def_start_date = '01/19'
        self.def_end_date = '02/19'
        self.def_single = False

    def _new_group(self, name):
        group = self.parser.add_argument_group(name)
        return group

    def _download_group(self):
        group = self.new_group('Download Configs')

        group.add_argument('-s', '--single', dest='single',
                           default=self.def_single, type=bool,
                           help='Download a single DODF pdf file.')

        group.add_argument('-sd', '--start_date', dest='start_date',
                           default=self.def_start_date, type=str,
                           help='Input the date in either mm/yy or mm-yy.')

        group.add_argument('-ed', '--end_date', dest='end_date',
                           default=self.def_end_date, type=str,
                           help='Input the date in either mm/yy or mm-yy.')

        return group

    def parse(self):
        """."""
        self._download_group()
        return self.parser.parse_args()
