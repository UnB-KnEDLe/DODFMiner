"""."""

import os
import tqdm
import requests
import urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta


MONTHS_STRING = ["", "01_Janeiro", "02_Fevereiro", "03_Março", "04_Abril",
                 "05_Maio", "06_Junho", "07_Julho", "08_Agosto",
                 "09_Setembro", "10_Outubro", "11_Novembro", "12_Dezembro"]


class Fetcher(object):
    """Responsible for download the DODF Pdfs"""

    def __init__(self, single=False):
        """."""
        self.save_path = './data'
        self.download_path = os.path.join(self.save_path, 'dodfs')
        self.prog_bar = None

    def _string_to_date(self, date):
        if '/' in date:
            date = datetime.strptime(date, '%m/%y').date()
        elif '-' in date:
            date = datetime.strptime(date, '%m-%y').date()
        else:
            msg = 'start_date or end_date must be in format mm/yy or mm-yy'
            raise Exception(msg)

        return date

    def _create_single_folder(self, path):
        if os.path.exists(path):
            self._log(os.path.basename(path) + " folder already exist")
        else:
            try:
                os.mkdir(path)
            except OSError as error:
                self._log("Exception during the directory creation")
                self._log(str(error))
            else:
                basename = os.path.basename(path)
                self._log(basename + " directory successful created")

    def _create_download_folder(self):
        self._create_single_folder(self.download_path)

    def _make_url(self, date):
        url_string = "http://www.buriti.df.gov.br/ftp/default.asp?ano="
        url_string += str(date.year)
        url_string += "&mes=" + str(MONTHS_STRING[date.month])
        url = urllib.parse.quote(url_string, safe=':/?=&')
        url = url.replace('%C3%A7', '%E7')  # Replace ç for %E7

        return url

    def _make_href_url(self, href):
        url = "http://www.buriti.df.gov.br/ftp/"
        url += href
        url = urllib.parse.quote(url, safe=':/?=&')
        url = url.replace('%C2', '')
        url = url.replace('3%8', '')
        url = url.replace('%C3%A7', '%E7')

        return url

    def _make_download_url(self, href):
        url = "http://www.buriti.df.gov.br/ftp/"
        download_url = url + href
        download_url = urllib.parse.quote(download_url, safe=':/?=&')

        return download_url

    def _fail_request_message(self, url, error):
        self._log(error)
        message = "Please check your internet connection, and " \
        "check if the url is online via browser: {}".format(url)
        self._log(message)

    def _get_soup_link(self, url):
        headers = {'User-Agent': 'Chrome/71.0.3578.80'}
        try:
            response = requests.get(url, headers=headers)
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as error:
            self._fail_request_message(url, error)

    def _file_exist(self, path):
        if os.path.exists(path):
            self._log(os.path.basename(path) + " file already exist")
            return True
        else:
            return False

    def _download_pdf(self, url, path):
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as error:
            self._fail_request_message(url, error)
        else:
            pdf_file = Path(path)
            pdf_file.write_bytes(response.content)
            self._log("Finished " + os.path.basename(path))

    def _make_month_path(self, year, actual_date):
        year_path = os.path.join(self.download_path,
                                 str(actual_date.year))
        if year != actual_date.year:
            self._create_single_folder(year_path)
        month_path = os.path.join(year_path,
                                  MONTHS_STRING[actual_date.month])

        return month_path

    def pull(self, start_date, end_date):
        """Start the download of the DODF pdfs.

        All dodfs are downloaded from start_date to end_date inclusively.
        The Pdfs are saved in a folder called "data" inside the project folder.

        Note:
            The name or the path of the save folder are hard coded and can't
            be changed due to some nonsense software engineer decision.

        Args:
            start_date (str): the start date in format mm/yy
            end_date (str): the start date in format mm/yy

        Returns:
            None
        """
        start_date = self._string_to_date(start_date)
        end_date = self._string_to_date(end_date)
        months_amt = ((end_date.year - start_date.year) * 12
                      + (end_date.month - start_date.month))
        self.prog_bar = tqdm.tqdm(total=months_amt+1, position=0)
        self._create_download_folder()
        year = 0
        for month in range(months_amt+1):
            actual_date = start_date + relativedelta(months=+month)
            desc_bar = str(actual_date)
            self.prog_bar.set_description("Date %s" % desc_bar)
            month_path = self._make_month_path(year, actual_date)
            self._create_single_folder(month_path)
            url = self._make_url(actual_date)
            a_list = self._get_soup_link(url)
            year = actual_date.year

            for a in a_list.find_all('a', href=True):
                a_url = self._make_href_url(a['href'])
                download_page = self._get_soup_link(a_url)
                number_of_files = int(download_page.find_all('b')[1].text)
                dodf_path = month_path
                if number_of_files > 1:
                    dodf_path = os.path.join(month_path, a.text)
                    self._create_single_folder(dodf_path)

                for a_href in download_page.find_all('a', href=True):
                    download_url = self._make_download_url(a_href['href'])
                    dodf_name_path = os.path.join(dodf_path, a_href.text)
                    if not self._file_exist(dodf_name_path):
                        self._log("Downloding "
                                  + os.path.basename(dodf_name_path))
                        self._download_pdf(download_url, dodf_name_path)
                    else:
                        self._log("File already exist "
                                  + os.path.basename(dodf_name_path)
                                  + " jumping to the next")

            self.prog_bar.update(1)

    def _log(self, message):
        self.prog_bar.write("[FETCHER] " + str(message))
