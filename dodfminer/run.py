#!/usr/bin/env python3

"""Main application module.

Contains class miner which is an interface to handle all extraction tasks.

Usage example::

    dodfminer --help

"""


from dodfminer.cli import CLI
from dodfminer.downloader.core import Downloader
from dodfminer.extract.pure.core import ContentExtractor
from dodfminer.extract.polished.helper import extract_multiple_acts, extract_multiple_acts_parallel, \
    extract_multiple_acts_with_committee, xml_multiple


class Miner():
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
        self.cli = CLI()
        self.args = self.cli.parse()

    def download(self):
        """Download PDFs with parameters from CLI."""
        downloader = Downloader(save_path=self.args.save_path)
        downloader.pull(self.args.start_date, self.args.end_date)

    def extract_content(self):
        """Extract Content from PDFs."""
        if self.args.single_file is None:
            if self.args.type_of_extr is not None:
                if self.args.type_of_extr == 'pure-text':
                    ContentExtractor.extract_to_txt(
                        folder=self.args.input_folder)
                elif self.args.type_of_extr == 'with-titles':
                    ContentExtractor.extract_to_json(folder=self.args.input_folder,
                                                     titles_with_boxes=True)
                elif self.args.type_of_extr == 'blocks':
                    ContentExtractor.extract_to_json(
                        folder=self.args.input_folder)
            elif self.args.act != 'all':
                if self.args.committee:
                    extract_multiple_acts_with_committee(self.args.input_folder, self.args.act, self.args.backend)
                elif self.args.number_of_processes is not None:
                    extract_multiple_acts_parallel(self.args.input_folder, self.args.act, self.args.backend, self.args.number_of_processes)
                else:
                    extract_multiple_acts(self.args.input_folder, self.args.act, self.args.backend)
            elif self.args.xml is not False:
                xml_multiple(self.args.input_folder, self.args.backend)
            else:
                self.cli.extract_content_parser.print_help()
        elif self.args.single_file is not None:
            self._extract_single_file()

    def _extract_single_file(self):
        if self.args.type_of_extr is not None:
            if self.args.type_of_extr == 'pure-text':
                ContentExtractor.extract_text(self.args.single_file,
                                              single=True)
            elif self.args.type_of_extr == 'with-titles':
                ContentExtractor.extract_structure(self.args.single_file,
                                                   single=True)
            elif self.args.type_of_extr == 'blocks':
                ContentExtractor.extract_text(
                    self.args.single_file, single=True, block=True)
        elif self.args.act != 'all':
            if self.args.committee:
                extract_multiple_acts_with_committee(self.args.single_file, self.args.act, self.args.backend)
            elif self.args.number_of_processes is not None:
                extract_multiple_acts_parallel(self.args.single_file, self.args.act, self.args.backend, self.args.number_of_processes)
            else:
                extract_multiple_acts(self.args.single_file, self.args.act, self.args.backend)
        elif self.args.xml is not False:
            xml_multiple(self.args.single_file, self.args.backend)
        else:
            self.cli.extract_content_parser.print_help()

    @classmethod
    def _log(cls, msg):
        print(f"[DODFMiner] {msg}")


def run():
    miner = Miner()
    if miner.args.subparser_name == 'downloader':
        miner.download()
    elif miner.args.subparser_name == 'extract':
        miner.extract_content()
    else:
        miner.cli.parser.print_help()


if __name__ == '__main__':
    run()
