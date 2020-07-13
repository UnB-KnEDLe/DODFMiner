#!/usr/bin/env python3

"""Main application module.

Contains class miner which is an interface to handle all extraction tasks.

Usage example::

    dodfminer --help
    
"""

from dodfminer.downloader.core import Downloader
from dodfminer.extract.core import ContentExtractor
from dodfminer.cli import CLI

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
        self.args = CLI().parse()

    def download(self):
        """Download PDFs with parameters from CLI."""
        downloader = Downloader(save_path=self.args.save_path)
        downloader.pull(self.args.start_date, self.args.end_date)

    def extract_content(self):
        """Extract Content from PDFs."""
        if self.args.type_of_extr == 'pure-text':
            ContentExtractor.extract_to_txt(folder=self.args.input_folder)
        elif self.args.type_of_extr == 'with-titles':
            ContentExtractor.extract_to_json(folder=self.args.input_folder,
                                             titles_with_boxes=True)
        elif self.args.type_of_extr == 'blocks':
            ContentExtractor.extract_to_json(folder=self.args.input_folder)

    def _log(self, msg):
        print(f"[DODFMiner] {msg}")


def run():
    miner = Miner()
    if miner.args.subparser_name == 'downloader':
        miner.download()
    elif miner.args.subparser_name == 'extract':
        miner.extract_content()
    else:
        miner._log("Program mode not recognized")
