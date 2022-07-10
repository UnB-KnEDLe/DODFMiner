# coding=utf-8

"""Download DODFs from the Buriti Website or models and pre-trained
   embeddings from the KnEDLe serve and save on proper directory.

Download monthly pdfs of DODFs or models and pre-trained embeddings.

Usage example::

    downloader = Downloader()
    downloader.pull(type_downloader, start_date, end_date)
    downloader.pull(type_downloader, act_id, model_type)
    downloader.pull(type_downloader, embedding_id)

"""

import os
from pathlib import Path
from datetime import datetime
import tqdm
import requests

from dateutil.relativedelta import relativedelta
from dodfminer.downloader.helper import check_date, get_downloads
from dodfminer.downloader.embeddings.base import Embeddings
from dodfminer.downloader.acts.abono import AbonoPermanencia
from dodfminer.downloader.acts.aditamento import Aditamentos
from dodfminer.downloader.acts.cessoes import Cessoes
from dodfminer.downloader.acts.contrato import Contratos
from dodfminer.downloader.acts.exoneracao import Exoneracao
from dodfminer.downloader.acts.nomeacao import Nomeacao
from dodfminer.downloader.acts.aposentadoria import Retirements
from dodfminer.downloader.acts.reversoes import Revertions
from dodfminer.downloader.acts.sem_efeito_aposentadoria import SemEfeitoAposentadoria
from dodfminer.downloader.acts.substituicao import Substituicao

MONTHS_STRING = ["", "01_Janeiro", "02_Fevereiro", "03_Março", "04_Abril",
                 "05_Maio", "06_Junho", "07_Julho", "08_Agosto",
                 "09_Setembro", "10_Outubro", "11_Novembro", "12_Dezembro"]

_acts_ids = {
    "Abono": AbonoPermanencia,
    "Aditamento": Aditamentos,
    "Aposentadoria": Retirements,
    "Cessoes": Cessoes,
    "Contrato": Contratos,
    "Exoneracao": Exoneracao,
    "Nomeacao": Nomeacao,
    "Reversoes": Revertions,
    "SemEfeitoAposentadoria": SemEfeitoAposentadoria,
    "Substituicao": Substituicao
}

class Downloader:
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

        f_path = os.path.dirname(__file__)
        self._model_path_prop = os.path.join(f_path, '../extract/polished/acts/prop_models')
        self._model_path_seg = os.path.join(f_path, '../extract/polished/acts/seg_models')
        self._create_single_folder(self._model_path_prop)
        self._create_single_folder(self._model_path_seg)

        self._embedding_path = os.path.join(f_path, '../extract/polished/acts/embeddings')
        self._create_single_folder(self._embedding_path)

    @classmethod
    def _string_to_date(cls, date):
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
                  f"check if the url is online via browser: {url}"
        self._log(message)

    def _file_exist(self, path, log=True):
        """Check if a file exists.

        Prevents redownloads.

        Args:
            path (str): The path where the file might be

        Returns:
            Boolean indicating if file does really exists.

        """
        if os.path.exists(path):
            if log:
                self._log(os.path.basename(path) + " file already exist")
            return True

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
        except requests.exceptions.HTTPError as error:
            self._fail_request_message(url, error)
        except requests.exceptions.RequestException as error:
            self._fail_request_message(url, error)
        else:
            pdf_file = Path(f"{path}.pdf")
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
        month_path = os.path.join(year_path, MONTHS_STRING[actual_date.month])

        return month_path

    def _pull_dodfs(self, start_date, end_date):
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
            self._prog_bar.set_description(f"Date {desc_bar}")
            month_path = self._make_month_path(year, actual_date)
            year = actual_date.year
            year_ = str(year)
            month_ = MONTHS_STRING[actual_date.month]

            if check_date(year_, month_) is True:
                self._create_single_folder(month_path)
            else:
                print(
                    f"*** There are still no DODFs for that date: {actual_date.month}/{year_} ***")
                continue

            self._get_dodfs(get_downloads(year_, month_), month_path)

        self._prog_bar.update(1)
    
    def _pull_models(self, act_id, model_type):
        """Make the download of the models.

        All model files are downloaded and saved inside the polished
        extractor folder.

        Args:
            act_id (str): The ID of the act whose models must be downloaded.
            model_type (str): The model type to be downloaded.

        Note:
            The name or the path of the save folder are hard coded and can't
            be changed due to how the models are loaded by the extractor.

        """
        self._download_model(act_id, model_type)

    def _pull_embeddings(self, embedding_id):
        """Make the download of the pre-trained-embeddings.

        All pre-trained embedding files are downloaded and saved
        inside the polished extractor folder.

        Args:
            embedding_id (str): The id of the pre-trained embedding to be downloaded.

        Note:
            The name or the path of the save folder are hard coded and can't
            be changed due to how the models are loaded by the extractor.

        """
        self._download_embedding(embedding_id)

    def pull(self, type_downloader="dodfs", start_date="01/19", end_date="01/19", act_id="all", model_type="prop", embedding_id="all"):
        """Make the download of the data (DODFs pdfs, models or
           pre-trained-embeddings).

        Args:
            type_downloader (str): The type of data to be downloaded.
            start_date (str): The start date in format mm/yyyy.
            end_date (str): The start date in format mm/yyyy.
            act_id (str): The ID of the act whose models must be downloaded.
            model_type (str): The model type to be downloaded.
            embedding_id (str): The id of the pre-trained embedding to be downloaded.

        """
        if type_downloader == "dodfs":
            self._pull_dodfs(start_date, end_date)
        elif type_downloader == "models":
            self._pull_models(act_id, model_type)
        elif type_downloader == "embeddings":
            self._pull_embeddings(embedding_id)

    def _get_dodfs(self, _links_for_each_dodf, month_path):
        """Create folder and stores the DODFs pdfs.

        Args:
            _links_for_each_dodf (dict): a dicts with links for each DODF.
            month_path (str): path to store DODFs pdfs.

        """
        for dodf_name, links in _links_for_each_dodf.items():
            dodf_path = month_path

            if len(links) > 1:
                dodf_path = os.path.join(month_path, dodf_name)
                self._create_single_folder(dodf_path)

            index = 0
            for link in links:
                index += 1
                download_link = link
                if len(links) == 1:
                    dodf_name_path = os.path.join(dodf_path, dodf_name)
                else:
                    dodf_name_path = os.path.join(
                        dodf_path, f'{dodf_name} {index}')

                if not self._file_exist(dodf_name_path):
                    self._log("Downloding " +
                                os.path.basename(dodf_name_path))
                    self._download_pdf(download_link, dodf_name_path)
                else:
                    self._log("Jumping to the next")

    def get_download_path(self):
        return self._download_path

    def _log(self, message):
        """Logs a message following the downloader pattern.

        Args:
            message (str): The message to be logged.

        """
        self._prog_bar.write("[DOWNLOADER] " + str(message))

    def _download_model(self, act_id, model_type):
        """Create folder and stores the models.

        Args:
            act_id (str): The ID of the act whose models must be downloaded.
            model_type (str): The model type to be downloaded.

        """
        if act_id == "all":
            self._download_all_models()
        else:
            if model_type == 'prop':
                act_model_path = os.path.join(self._model_path_prop, act_id)
            elif model_type == 'seg':
                act_model_path = os.path.join(self._model_path_seg, act_id)

            self._create_single_folder(act_model_path)

            self._log('downloading model')
            _acts_ids[act_id](act_model_path, model_type)
            self._log(act_id + ' model downloaded')

    def _download_embedding(self, embedding_id):
        """Create folder and stores the pre-trained embedding files.

        Args:
            embedding_id (str): The id of the pre-trained embedding to be downloaded.

        """
        if embedding_id == "all":
            self._download_all_embeddings()
        else:
            self._log('downloading pre-trained embedding')
            Embeddings(self._embedding_path, embedding_id)
            self._log(embedding_id + ' embedding downloaded')

    def _download_all_models(self):
        """Download all available models (of all possible types)."""
        for ato_id in _acts_ids:
            for model_type in ['prop', 'seg']:
                self._download_model(ato_id, model_type)

    def _download_all_embeddings(self):
        """Download all available pre-trained embeddings."""
        available_embeddings = Embeddings.get_ids()

        for emb in available_embeddings:
            self._download_embedding(emb)

if __name__ == '__main__':
    downloader = Downloader(save_path='./')
    downloader.pull(start_date="05/2021", end_date="06/2021")
