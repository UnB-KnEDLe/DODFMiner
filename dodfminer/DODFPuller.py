from datetime import datetime
from dateutil.relativedelta import *
import os
import urllib.parse
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import tqdm

MONTHS_STRING = ["", "01_Janeiro", "02_Fevereiro", "03_Março", "04_Abril",
                    "05_Maio", "06_Junho", "07_Julho", "08_Agosto",
                    "09_Setembro", "10_Outubro", "11_Novembro", "12_Dezembro"]

class DODFPuller(object):
    def __init__(self, save_path='./'):
        self.save_path = save_path
        self.download_path = os.path.join(self.save_path, 'DODF_downloads')
        self.prog_bar = None

    def __string_to_date(self, date):
        if '/' in date:
            date = datetime.strptime(date, '%m/%Y').date()
        elif '-' in date:
            date = datetime.strptime(date, '%m-%Y').date()
        else:
            raise Exception('start_date or end_date must be in format m/Y or m-Y')

        return date

    def __create_single_folder(self, path):
        if os.path.exists(path):
            self.log(os.path.basename(path) + " folder already exist")
        else:
            try:
                os.mkdir(path)
            except OSError as error:
                self.log("Exception during the directory creation")
                self.log(str(error))
            else:
                self.log(os.path.basename(path) + " directory successful created")

    def __create_download_folder(self):
        self.__create_single_folder(self.download_path)

    def __make_url(self, date):
        url_string = "http://www.buriti.df.gov.br/ftp/default.asp?ano="
        url_string += str(date.year)
        url_string += "&mes=" + str(MONTHS_STRING[date.month])
        url = urllib.parse.quote(url_string, safe =':/?=&')
        url = url.replace('%C3%A7', '%E7') # Replace ç for %E7

        return url

    def __make_href_url(self, href):
        url = "http://www.buriti.df.gov.br/ftp/"
        url += href
        url = urllib.parse.quote(url, safe =':/?=&')
        url = url.replace('%C2', '')
        url = url.replace('3%8', '')
        url = url.replace('%C3%A7', '%E7')

        return url

    def __make_download_url(self, href):
        url = "http://www.buriti.df.gov.br/ftp/"
        download_url = url + href
        download_url = urllib.parse.quote(download_url, safe =':/?=&')

        return download_url

    def __get_soup_link(self, url):
        headers = {'User-Agent': 'Chrome/71.0.3578.80'}
        response = requests.get(url, headers=headers)

        return BeautifulSoup(response.text, "html.parser")

    def __file_exist(self, path):
        if os.path.exists(path):
            self.log(os.path.basename(path) + " file already exist")
            return True
        else:
            return False

    def __download_pdf(self, url, path):
        pdf_file = Path(path)
        response = requests.get(url)
        pdf_file.write_bytes(response.content)

    def pull(self, start_date, end_date):

        start_date = self.__string_to_date(start_date)
        end_date = self.__string_to_date(end_date)
        numb_of_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        self.prog_bar = tqdm.tqdm(total=numb_of_months, position=0)
        self.__create_download_folder()
        year = 0
        for month in range(numb_of_months+1):
            actual_date = start_date + relativedelta(months=+month)
            desc_bar = str(actual_date)
            self.prog_bar.set_description("Date %s" % desc_bar)
            if year != actual_date.year:
                year_path = os.path.join(self.download_path, str(actual_date.year))
                self.__create_single_folder(year_path)

            month_path = os.path.join(year_path, MONTHS_STRING[actual_date.month])
            self.__create_single_folder(month_path)
            url = self.__make_url(actual_date)
            a_list = self.__get_soup_link(url)

            for a in a_list.find_all('a', href=True):
                a_url = self.__make_href_url(a['href'])
                download_page = self.__get_soup_link(a_url)
                number_of_files = int(download_page.find_all('b')[1].text)
                dodf_path = month_path
                if number_of_files > 1:
                    dodf_path = os.path.join(month_path, a.text)
                    self.__create_single_folder(dodf_path)

                for a_href in download_page.find_all('a', href=True):
                    download_url = self.__make_download_url(a_href['href'])
                    dodf_name_path = os.path.join(dodf_path, a_href.text)
                    if not self.__file_exist(dodf_name_path):
                        self.__download_pdf(download_url, dodf_name_path)
                        self.log("Downloding " + os.path.basename(dodf_name_path))
                    else:
                        self.log("File already exist "
                                    + os.path.basename(dodf_name_path) +
                                    " jumping to the next")

            year = actual_date.year
            self.prog_bar.update(1)
            # print(MONTHS_STRING[actual_date.month])


    def log(self, message):
        # print("[DODFPuller] " + str(message))
        self.prog_bar.write("[DODFPuller] " + str(message))

#puller = DODFPuller('./')
#puller.pull('01-2015', '05-2015')
