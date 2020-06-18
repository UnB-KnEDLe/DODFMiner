# coding=utf-8

"""Extract content from DODFS and export to JSON.

Contains class ContentExtractor which have to public functions
avaiable to extract the DODF to JSON

Typical usage example:
    ContentExtractor.extract_to_json()
    ContentExtractor.extract_content(file)
"""

import os
import time
import json
import fitz
import unicodedata

from pathlib import Path
from difflib import SequenceMatcher

from dodfminer.prextract.title_extractor import ExtractorTitleSubtitle
from dodfminer.prextract.box_extractor import get_doc_text_boxes

TMP_PATH = "./data/tmp/"
RESULTS_PATH = "./data/results/"
TMP_PATH_IMAGES = "./data/tmp/images"
RESULTS_PATH_JSON = "./data/results/json"
RESULTS_PATH_TXT = "./data/results/txt"

class ContentExtractor:
    """Extract content from DODFs and export to JSON.

    Extracts content from DODF using as suport the title and subtitle
    databases (which runs using MuPDF) and the Tesseract OCR library. All the
    contents are exported to a JSON in which it's keys are DODFs titles or
    subtitles, and its values are the correspondent content.

    Note:
        This class is not constructable, it cannot generate objects.

    """

    @classmethod
    def extract_text(cls, file, block=False, sep=' '):
        return cls._drawboxes_extraction(file, block=block, sep=sep)

    @classmethod
    def extract_structure(cls, file):
        return cls._extract_boxes_with_title(file)

    @classmethod
    def extract_to_txt(cls):
        """Extract information from DODF to TXT.

        For each pdf file in data/dodfs, extract information from the
        pdf and output it to txt.

        """
        pdfs_path_list = cls._get_pdfs_list()
        cls._create_single_folder(RESULTS_PATH)
        cls._create_single_folder(RESULTS_PATH_TXT)
        txt_path_list = cls._get_txt_list()

        for file in pdfs_path_list:
            pdf_name = os.path.splitext(os.path.basename(file))[0]
            if pdf_name not in txt_path_list:
                cls._log(pdf_name)
                text = cls.extract_text(file)
                t_path = cls._struct_txt_subfolders(file)
                f = open(RESULTS_PATH_TXT + '/' + t_path, "w")
                f.write(text)
            else:
                cls._log("TXT already exists")

    @classmethod
    def extract_to_json(cls, titles_with_boxes=False):
        """Extract information from DODF to JSON.

        For each pdf file in data/dodfs, extract information from the
        pdf and output it to json.

        """
        # Get list of all downloaded pdfs
        pdfs_path_list = cls._get_pdfs_list()
        # Get list of existing json to not repeat work
        json_path_list = cls._get_json_list()

        cls._create_single_folder(TMP_PATH)
        cls._create_single_folder(RESULTS_PATH)
        cls._create_single_folder(RESULTS_PATH_JSON)
        cls._create_single_folder(RESULTS_PATH_TXT)

        for file in pdfs_path_list:
            pdf_name = os.path.splitext(os.path.basename(file))[0]
            # We do not want the system to repeat itself doing the same work
            if pdf_name not in json_path_list:
                # TODO(Khalil009) Include a CLI Flag to make only
                # low cost extractions
                if os.path.getsize(file) < 30000000:  # Remove in future.
                    # Remove images that might still there from previous exec
                    cls._log(pdf_name)
                    if titles_with_boxes:
                        content = cls.extract_structure(file)
                    else:
                        content = cls.extract_text(file, block=True)

                    j_path = cls._struct_json_subfolders(file)
                    json.dump(content, open(RESULTS_PATH_JSON + '/' + j_path, "w",
                                                 encoding="utf-8"), ensure_ascii=False)
            else:
                cls._log("JSON already exists")

    @classmethod
    def _extract_boxes_with_title(cls, file):
        content_dict = {}
        try:
            title_base = cls._extract_titles(file).json.keys() 
        except Exception as e:  
            cls._log(e)
        else:
            boxes = cls._drawboxes_extraction(cls, file, block=True)
            first_title = False
            is_title = False
            actual_title = ''
            for box in boxes:
                text = box[4]
                for title in title_base:
                    title.replace("\n", "")
                    if text == title:
                        first_title = True
                        is_title = True
                        actual_title = title
                        if title not in content_dict.keys():
                            content_dict.update({title: []})
                    else:
                        is_title = False

                if first_title and not is_title:
                    if int(box[1]) != 55 and int(box[1]) != 881:
                        content_dict[actual_title].append(box[:5])

            return content_dict

    @classmethod
    def _drawboxes_extraction(cls, file, block=False, sep=' '):
        drawboxes_text = ''
        list_of_boxes = []
        pymu_file = fitz.open(file)
        for textboxes in get_doc_text_boxes(pymu_file):
            for text in textboxes:
                if int(text[1]) != 55 and int(text[1]) != 881:
                    if block:
                        list_of_boxes.append(text)
                    else:   
                        drawboxes_text += (text[4] + sep)

        if block:
            return list_of_boxes
        else:
            drawboxes_text = unicodedata.normalize('NFKD', drawboxes_text).encode('ascii', 'ignore').decode('utf8')
            return drawboxes_text

    @classmethod
    def _extract_titles(cls, file):
        """Extract titles and subtitles from the DODF.

        Args:
            file: The DODF to extract the titles.

        Returns:
            An object of type ExtractorTitleSubtitle, in which have the
            attributes:

            titles: get all titles from pdf
            subtitle: get all subtitles from pdf

        Raises:
            Exception: error in extracting titles from pdf

        """
        try:
            title_database = ExtractorTitleSubtitle(file)
            cls._log(file)
        except Exception as e:
            cls._log(f"Error in extracting files from {file}: {e}")
            raise
        else:
            return title_database

    @classmethod
    def _get_pdfs_list(cls):
        """Get DODFs list from the path.

        Returns:
            A list of DODFS' pdfs paths.

        """
        pdfs_path_list = []
        for dp, _, fn in os.walk(os.path.expanduser('./data/dodfs')):
            for f in fn:
                pdfs_path_list.append(os.path.join(dp, f))

        return pdfs_path_list

    @classmethod
    def _get_json_list(cls):
        """Get list of exisiting JSON from the path.

        Returns:
            A list of all exisiting JSON's.

        """
        aux = []
        for dp, _, fn in os.walk(os.path.expanduser(RESULTS_PATH_JSON)):
            for f in fn:
                aux.append(os.path.join(dp, f))

        json_path_list = []
        for file in aux:
            json_path_list.append(os.path.splitext(os.path.basename(file))[0])

        return json_path_list

    @classmethod
    def _get_txt_list(cls):
        """Get list of exisiting TXT from the path.

        Returns:
            A list of all exisiting TXT's.

        """
        aux = []
        for dp, _, fn in os.walk(os.path.expanduser(RESULTS_PATH_TXT)):
            for f in fn:
                aux.append(os.path.join(dp, f))

        txt_path_list = []
        for file in aux:
            txt_path_list.append(os.path.splitext(os.path.basename(file))[0])

        return txt_path_list

    @classmethod
    def _struct_json_subfolders(cls, path):
        """Create directory for the JSON.

        Using the same standart from the DODFs directory tree. Create the
        JSONs folder as same.

        Raises:
            FileExistsError: The folder being created is already there.

        Return:
            The path created for the JSON to be saved.

        """
        splited = path.split('/')
        splited = splited[3:]
        basename = splited[-1].split('.')
        basename = basename[0] + '.json'
        splited[-1] = basename
        final_path = '/'.join(splited)
        path = Path(RESULTS_PATH_JSON + '/' + '/'.join(splited[:-1]))
        try:
            path.mkdir(parents=True)
        except FileExistsError:
            pass

        return final_path

    @classmethod
    def _struct_txt_subfolders(cls, path):
        """Create directory for the TXT.

        Using the same standart from the DODFs directory tree. Create the
        TXTs folder as same.

        Raises:
            FileExistsError: The folder being created is already there.

        Return:
            The path created for the TXT to be saved.

        """
        splited = path.split('/')
        splited = splited[3:]
        basename = splited[-1].split('.')
        basename = basename[0] + '.txt'
        splited[-1] = basename
        final_path = '/'.join(splited)
        path = Path(RESULTS_PATH_TXT + '/' + '/'.join(splited[:-1]))
        try:
            path.mkdir(parents=True)
        except FileExistsError:
            pass

        return final_path

    @classmethod
    def _create_single_folder(cls, path):
        """Create a single folder given the directory path.

        This function might create a folder, observe that the folder already
        exists, or raise an error if the folder cannot be created.

        Args:
            path: The path to be created

        Raises:
            OSError: Error creating the directory.

        """
        if os.path.exists(path):
            cls._log(os.path.basename(path) + " folder already exist")
        else:
            try:
                os.mkdir(path)
            except OSError as error:
                cls._log("Exception during the directory creation")
                cls._log(str(error))
            else:
                basename = os.path.basename(path)
                cls._log(basename + " directory successful created")

    @classmethod
    def _log(cls, msg):
        print(f"[EXTRACTOR] {msg}")