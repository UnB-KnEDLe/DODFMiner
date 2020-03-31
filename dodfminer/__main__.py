"""Main application module.

Contains class miner which is an interface to handle all extraction tasks.

Typical usage example:
    From DODFMiner execute:
    python3 dodfminer

"""

from cli import CLI
from downloader.fetcher import Fetcher
from extract.content_extractor import ContentExtractor


class Miner(object):
    """Main DODFMiner class.

    The Miner class is a interface that handles download, pre-extraction,
    and extraction of DODFs.

    Attributes:
        start_date: Argument start_date from CLI
        end_date: Argument end_date from CLI
        single: Argument single from CLI
        ext_content: Argument extract_content from CLI

    """

    def __init__(self):
        """Init Miner class to handle all the extraction process."""
        args = CLI().parse()
        self.start_date = args.start_date
        self.end_date = args.end_date
        self.single = args.single
        self.ext_content = args.extract_content

    def download(self):
        """Download PDFs with parameters from CLI."""
        fetcher = Fetcher(single=self.single)
        fetcher.pull(self.start_date, self.end_date)

    def extract_content(self):
        """Extract Content from PDFs."""
        ContentExtractor.extract_to_json()


if __name__ == '__main__':
    miner = Miner()
    if miner.ext_content:
        miner.extract_content()
    else:
        miner.download()
