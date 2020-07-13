# coding=utf-8

"""Extract content from DODFS and export to JSON.

Contains class ContentExtractor which have to public functions
avaiable to extract the DODF to JSON

Usage example::

    pdf_text = ContentExtractor.extract_text(file)
    ContentExtractor.extract_to_txt(folder)

"""

import os
import json
import unicodedata

from pathlib import Path

import fitz

from dodfminer.extract.pure.utils.title_extractor import ExtractorTitleSubtitle
from dodfminer.extract.pure.utils.box_extractor import get_doc_text_boxes

RESULTS_PATH = "results/"
RESULTS_PATH_JSON = "results/json"
RESULTS_PATH_TXT = "results/txt"


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
    def extract_text(cls, file, block=False, sep=' ', norm='NFKD'):
        """Extract block of text from file

        Args:
            file: The DODF to extract the titles.
            block: Extract the text as a list of text blocks

        Returns:
            A list of arrays if block is True or strign otherwise.
            Each array in the list have 5 values: the first four
            are the coordinates of the box (x0, y0, x1, y1) end the last
            is the text from the box.

            The string returned correspond to the text from all PDF.

        """
        drawboxes_text = ''
        list_of_boxes = []
        pymu_file = fitz.open(file)
        for textboxes in get_doc_text_boxes(pymu_file):
            for text in textboxes:
                if int(text[1]) != 55 and int(text[1]) != 881:
                    if block:
                        norm_text = cls._normalize_text(text[4], norm)
                        list_of_boxes.append((text[0], text[1], text[2],
                                              text[3], norm_text))
                    else:
                        drawboxes_text += (text[4] + sep)

        if block:
            return list_of_boxes

        drawboxes_text = cls._normalize_text(drawboxes_text, norm)
        return drawboxes_text

    @classmethod
    def extract_structure(cls, file, norm='NFKD'):
        """Extract boxes of text with your respective titles.

        Args:
            file: The DODF to extract the titles.

        Returns:
            A dictionaty with the blocks organized by title

            Example::

                {
                    "Title": [
                        [
                            x0,
                            y0,
                            x1,
                            y1,
                            "Text"
                        ]
                    ],
                    ...
                }

        """
        content_dict = {}
        try:
            title_base = cls._extract_titles(file).json.keys()
        except Exception as e:
            cls._log(e)
        else:
            boxes = cls.extract_text(file, block=True, norm=norm)
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
    def extract_to_txt(cls, folder='./', norm='NFKD'):
        """Extract information from DODF to TXT.

        For each pdf file in data/dodfs, extract information from the
        pdf and output it to txt.

        """
        pdfs_path_list = cls._get_pdfs_list(folder)
        cls._create_single_folder(os.path.join(folder, RESULTS_PATH))
        cls._create_single_folder(os.path.join(folder, RESULTS_PATH_TXT))
        txt_path_list = cls._get_txt_list(folder)

        for file in pdfs_path_list:
            pdf_name = os.path.splitext(os.path.basename(file))[0]
            if pdf_name not in txt_path_list:
                cls._log(pdf_name)
                text = cls.extract_text(file, norm=norm)
                t_path = cls._struct_subfolders(file, False, folder)
                f = open(t_path, "w")
                f.write(text)
            else:
                cls._log("TXT already exists")

    @classmethod
    def extract_to_json(cls, folder='./',
                        titles_with_boxes=False, norm='NFKD'):
        """Extract information from DODF to JSON.

        Args:
            folder: The folder containing the PDFs to be extracted
            titles_with_boxes: Extract with titles
            norm: What normalization to use. Normalizations can be found
                  unicodedata library

        For each pdf file in data/dodfs, extract information from the
        pdf and output it to json.

        """
        # Get list of all downloaded pdfs
        pdfs_path_list = cls._get_pdfs_list(folder)
        # Get list of existing json to not repeat work
        json_path_list = cls._get_json_list(folder)

        cls._create_single_folder(os.path.join(folder, RESULTS_PATH))
        cls._create_single_folder(os.path.join(folder, RESULTS_PATH_JSON))

        for file in pdfs_path_list:
            pdf_name = os.path.splitext(os.path.basename(file))[0]
            # We do not want the system to repeat itself doing the same work
            if pdf_name not in json_path_list:
                # low cost extractions
                if os.path.getsize(file) < 30000000:  # Remove in future.
                    # Remove images that might still there from previous exec
                    cls._log(pdf_name)
                    if titles_with_boxes:
                        content = cls.extract_structure(file, norm=norm)
                    else:
                        content = cls.extract_text(file, block=True, norm=norm)
                    j_path = cls._struct_subfolders(file, True, folder)
                    json.dump(content, open(j_path, "w", encoding="utf-8"),
                              ensure_ascii=False)
            else:
                cls._log("JSON already exists")

    @classmethod
    def _normalize_text(cls, text, form='NFKD'):
        """Normalize text.

        Args:
            text: The text to be normalized.
            form: The normalized form accordingly to the unicodedata library'.

        Returns:
            A string with the normalized text.

        """
        normalized = unicodedata.normalize(form, text).encode('ascii', 'ignore').decode('utf8')
        return normalized

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
    def _get_pdfs_list(cls, folder):
        """Get DODFs list from the path.

        Returns:
            A list of DODFS' pdfs paths.

        """
        pdfs_path_list = []
        for dp, _, fn in os.walk(os.path.expanduser(os.path.join(folder))):
            for f in fn:
                if '.pdf' in f:
                    pdfs_path_list.append(os.path.join(dp, f))

        return pdfs_path_list

    @classmethod
    def _get_json_list(cls, folder):
        """Get list of exisiting JSON from the path.

        Returns:
            A list of all exisiting JSON's.

        """
        aux = []
        for dp, _, fn in os.walk(os.path.expanduser(os.path.join(folder, RESULTS_PATH_JSON))):
            for f in fn:
                aux.append(os.path.join(dp, f))

        json_path_list = []
        for file in aux:
            json_path_list.append(os.path.splitext(os.path.basename(file))[0])

        return json_path_list

    @classmethod
    def _get_txt_list(cls, folder):
        """Get list of exisiting TXT from the path.

        Returns:
            A list of all exisiting TXT's.

        """
        aux = []
        for dp, _, fn in os.walk(os.path.expanduser(os.path.join(folder, RESULTS_PATH_TXT))):
            for f in fn:
                aux.append(os.path.join(dp, f))

        txt_path_list = []
        for file in aux:
            txt_path_list.append(os.path.splitext(os.path.basename(file))[0])

        return txt_path_list

    @classmethod
    def _struct_subfolders(cls, path, json_f, folder):
        """Create directory for the JSON.

        Using the same standart from the DODFs directory tree. Create the
        JSONs folder as same.

        Raises:
            FileExistsError: The folder being created is already there.

        Return:
            The path created for the JSON to be saved.

        """
        type_f = '.json' if json_f else '.txt'
        res_path = RESULTS_PATH_JSON if json_f else RESULTS_PATH_TXT

        path = path.replace(folder, "")
        splited = path.split('/')
        basename = splited[-1].split('.')
        basename = basename[0] + type_f
        splited[-1] = basename
        final_path = '/'.join(splited[1:])
        final_path = os.path.join(folder, res_path, final_path)
        path = Path(os.path.join(folder, res_path, *splited[:-1]))
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
