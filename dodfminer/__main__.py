"""."""

from cli import CLI
from downloader.fetcher import Fetcher
from extract.content_extractor import ContentExtractor

class Miner(object):
    """."""

    def __init__(self):
        """."""
        args = CLI().parse()
        self.start_date = args.start_date
        self.end_date = args.end_date
        self.single = args.single
        self.ext_content = args.extract_content

    def download(self):
        """."""
        fetcher = Fetcher(single=self.single)
        fetcher.pull(self.start_date, self.end_date)

    def extract_content(self):
        """."""
        ContentExtractor.extract_to_json()


if __name__ == '__main__':

    miner = Miner()
    if miner.ext_content:
        miner.extract_content()
    else:
        miner.download()
