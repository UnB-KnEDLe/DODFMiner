"""Main application module.

Contains class miner which is an interface to handle all extraction tasks.

Typical usage example:
    From DODFMiner execute:
    python3 dodfminer

"""

from cli import GLOBAL_ARGS
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
        self.args = GLOBAL_ARGS

    def download(self):
        """Download PDFs with parameters from CLI."""
        fetcher = Fetcher(single=self.args.single)
        fetcher.pull(self.args.start_date, self.args.end_date)

    def extract_content(self):
        """Extract Content from PDFs."""
        ContentExtractor.extract_to_json()

    def _log(self, msg):
        print(f'[DODFMiner] {msg}')


if __name__ == '__main__':
    miner = Miner()
    if miner.args.subparser_name == 'download':
        miner.download()
    elif miner.args.subparser_name == 'prextract':
        miner._log("Prextract usage not Implemented")
    elif miner.args.subparser_name == 'extract':
        miner.extract_content()
