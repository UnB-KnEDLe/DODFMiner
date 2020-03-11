"""."""

from cli import CLI
from fetcher import Fetcher


class Miner(object):
    """."""

    def __init__(self):
        """."""
        args = CLI().parse()
        self.start_date = args.start_date
        self.end_date = args.end_date
        self.single = args.single

    def download(self):
        """."""
        fetcher = Fetcher(single=self.single)
        fetcher.pull(self.start_date, self.end_date)


if __name__ == '__main__':
    Miner().download()
