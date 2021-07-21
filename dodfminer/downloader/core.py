# coding=utf-8

"""Download DODFs from the Buriti Website and save on proper directory.

Download monthly pdfs of DODFs.

Usage example::

    downloader = Downloader()
    downloader.pull(start_date, end_date)

"""

import os
import tqdm
import requests

from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dodfminer.downloader.helper import check_date, get_downloads


MONTHS_STRING = ["", "01_Janeiro", "02_Fevereiro", "03_Março", "04_Abril",
                 "05_Maio", "06_Junho", "07_Julho", "08_Agosto",
                 "09_Setembro", "10_Outubro", "11_Novembro", "12_Dezembro"]


class Downloader(object):
    """Responsible for the download of the DODFs Pdfs.

    Args:
        save_path (str): Path to save the downloads.

    Attributes:
        _download_path: Folder in which the downloads will be stored.
        _prog_bar: Indicate if download should contain a progress bar.

    """

    def __init__(self, save_path='./'):
        self._prog_bar = tqdm.tqdm()
        self._create_single_folder(os.path.join(save_path, 'dodfs'))
        self._download_path = os.path.join(save_path, 'dodfs')

    def _string_to_date(self, date):
        """Convert the date to datetime.

        Args:
            date (:obj:`datetime`): The date to be converted in string format.

        Returns:
            Return the date formated in string now as datetime datatype.

        Raises:
            Exception: date passed through cli is in wrong format.

        """
        if '/' in date:
            date = datetime.strptime(date, '%m/%Y').date()
        elif '-' in date:
            date = datetime.strptime(date, '%m-%Y').date()
        else:
            msg = 'start_date or end_date must be in format mm/yyyy or mm-yyyy'
            raise Exception(msg)

        return date

    def _create_single_folder(self, path):
        """Create a single folder given the directory path.

        This function might create a folder, observe that the folder already
        exists, or raise an error if the folder cannot be created.

        Args:
            path (str): The path to be created

        Raises:
            OSError: Error creating the directory.

        """
        if os.path.exists(path):
            self._log(os.path.basename(path) + " folder already exist")
        else:
            try:
                os.mkdir(path)
            except OSError as error:
                self._log("Exception during the directory creation")
                self._log(str(error))
                raise
            else:
                basename = os.path.basename(path)
                self._log(basename + " directory successful created")

    def _create_download_folder(self):
        """Create Downloaded DODFs Structures."""
        # import pdb; pdb.set_trace()
        self._create_single_folder(self._download_path)

    def _fail_request_message(self, url, error):
        """Log error messages in download.

        Args:
            url (str): The failing url to the website.
            error (str): The kind of error happening.

        """
        self._log(error)
        message = "Please check your internet connection, and " \
                  "check if the url is online via browser: {}".format(url)
        self._log(message)

    def _file_exist(self, path):
        """Check if a file exists.

        Prevents redownloads.

        Args:
            path (str): The path where the file might be

        Returns:
            Boolean indicating if file does really exists.

        """
        if os.path.exists(path):
            self._log(os.path.basename(path) + " file already exist")
            return True
        else:
            return False

    def _download_pdf(self, url, path):
        """Download the DODF PDF.

        Note:
            Might be time consuming depending on bandwidth.

        Args:
            url (str): The pdf url.
            path (str): The path to save the pdf.

        Raises:
            RequestException: Error in case the request to download fails.

        """
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            self._fail_request_message(url, error)
        except requests.exceptions.HTTPError as error:
            self._fail_request_message(url, error)
        else:
            pdf_file = Path(path)
            pdf_file.write_bytes(response.content)
            self._log("Finished " + os.path.basename(path))

    def _make_month_path(self, year, actual_date):
        """Create and return the folder for the year and month being download.

        Args:
            year (int): The year respective to the folder.
            actual_date (:obj:`datetime`): The date in which the downloaded
            DODF corresponds.

        Returns:
            The path to the actual month in which the download is being made.

        """
        year_path = os.path.join(self._download_path,
                                 str(actual_date.year))
        if year != actual_date.year:
            self._create_single_folder(year_path)
        month_path = os.path.join(year_path,MONTHS_STRING[actual_date.month])

        return month_path

    def pull(self, start_date, end_date):
        """Make the download of the DODFs pdfs.

        All dodfs are downloaded from start_date to end_date inclusively.
        The Pdfs are saved in a folder called "data" inside the project folder.

        Args:
            start_date (str): The start date in format mm/yyyy.
            end_date (str): The start date in format mm/yyyy.

        Note:
            The name or the path of the save folder are hard coded and can't
            be changed due to some nonsense software engineer decision.

        """
        # Convert string to datetime and calculate ammount to be used in
        # progress bar
        start_date = self._string_to_date(start_date)
        end_date = self._string_to_date(end_date)
        months_amt = ((end_date.year - start_date.year) * 12
                      + (end_date.month - start_date.month))
        # Creates progress bar
        self._prog_bar = tqdm.tqdm(total=months_amt)
        # # Creates the project folder structure
        self._create_download_folder()
        year = 0

        
        for month in range(months_amt+1):
            actual_date = start_date + relativedelta(months=+month)
            desc_bar = str(actual_date)
            self._prog_bar.set_description("Date %s" % desc_bar)
            month_path = self._make_month_path(year, actual_date)
            year = actual_date.year
            year_ = str(year)
            month_ = MONTHS_STRING[actual_date.month]

            
            if(check_date(year_,month_) == True):
                self._create_single_folder(month_path)
            else:
                print(f"*** There are still no DODFs for that date: {actual_date.month}/{year_} ***")
                continue

            _links_for_each_dodf = get_downloads(year_,month_)

            for dodf in _links_for_each_dodf:
                dodf_name = dodf
                links = _links_for_each_dodf[dodf]
                dodf_path = month_path

                if(len(links) > 1):
                    dodf_path = os.path.join(month_path, dodf_name)
                    self._create_single_folder(dodf_path)
                
                x = 0
                for l in links:
                    x+=1
                    download_link = l 
                    if(len(links) == 1): 
                        dodf_name_path = os.path.join(dodf_path, dodf_name)
                    else:
                        dodf_name_path = os.path.join(dodf_path, f'{dodf_name} {x}')

                    if not self._file_exist(dodf_name_path):
                        self._log("Downloding "+ os.path.basename(dodf_name_path))
                        self._download_pdf(download_link, dodf_name_path)
                    else:
                        self._log("Jumping to the next")

        self._prog_bar.update(1)

    def _log(self, message):
        """Logs a message following the downloader pattern.

        Args:
            message (str): The message to be logged.

        """
        self._prog_bar.write("[DOWNLOADER] " + str(message))


if __name__ == '__main__':
    downloader = Downloader(save_path='./')
    downloader.pull(start_date="05/2021", end_date="06/2021")