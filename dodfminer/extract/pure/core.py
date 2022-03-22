# coding=utf-8

"""Extract content from DODFS and export to JSON.

Contains class ContentExtractor which have to public functions
avaiable to extract the DODF to JSON

Usage example::

    from dodfminer.extract.pure.core import ContentExtractor

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

    Extracts content from DODF files using as suport the title and subtitle
    databases—which runs using MuPDF—, and the Tesseract OCR library. All the
    content is exported to a JSON file, in which its keys are DODF titles or
    subtitles, and its values are the correspondent content.

    Note:
        This class is not constructable, it cannot generate objects.

    """

    @classmethod
    # pylint: disable=too-many-arguments
    def extract_text(cls, file, single=False, block=False, is_json=True, sep=' ', norm='NFKD'):
        """Extract block of text from file

        Args:
            file: The DODF to extract titles from.
            single: output content in a single file in the file directory.
            block: Extract the text as a list of text blocks.
            json: The list of text blocks are written as a json file.
            sep: The separator character between each block of text.
            norm: Type of normalization applied to the text.

        Note:
            To learn more about the each type of normalization used in the
            `unicode.normalization` method, `click here <https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize>`_.

        Returns:

            These are the outcomes for each parameter combination.

            When `block=True` and `single=True`:
                In case `json=True`, The method saves a JSON file containing the
                text blocks in the DODF file. However, is case `json=False`, the
                text from the whole PDF is saved as a string in a .txt file.

            When `block=True` and `single=False`:
                The method returns an array containing text blocks.

                Each array in the list have 5 values: the first four are the
                coordinates of the box from where the text was extracted
                (x0, y0, x1, y1), while the last is the text from the box.

                Example::

                    (127.77680206298828,
                    194.2507781982422,
                    684.0039672851562,
                    211.97523498535156,
                    "ANO XLVI EDICAO EXTRA No- 4 BRASILIA - DF")

            When `block=False` and `single=True`:
                The text from the whole PDF is saved in a .txt file as a
                normalized string.

            When `block=False` and `single=False`:
                The method returns a normalized string containing the
                text from the whole PDF.

        """
        drawboxes_text = ''
        list_of_boxes = []
        pymu_file = fitz.open(file)

        for page_boxes in get_doc_text_boxes(pymu_file):
            for text in page_boxes:
                if int(text[1]) != 55 and int(text[1]) != 881:
                    if block:
                        norm_text = cls._normalize_text(text[4], norm)
                        if is_json:
                            list_of_boxes.append((text[0], text[1], text[2],
                                                  text[3], norm_text))
                        else:
                            drawboxes_text += (norm_text + sep)
                    else:
                        drawboxes_text += (text[4] + sep)

        if block:
            if not single:
                return list_of_boxes
            if is_json:
                cls._save_single_file(file, 'json', json.dumps(list_of_boxes))
            else:
                return cls._save_single_file(file, 'txt', drawboxes_text)

        drawboxes_text = cls._normalize_text(drawboxes_text, norm)
        return drawboxes_text if not single else cls._save_single_file(file, 'txt', drawboxes_text)

    @classmethod
    def extract_structure(cls, file, single=False, norm='NFKD'): # pylint: disable=too-many-locals
        """Extract boxes of text with their respective titles.

        Args:
            file: The DODF file to extract titles from.
            single: Output content in a single file in the file directory.
            norm: `Type of normalization <https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize>`_ applied to the text.

        Returns:
            A dictionaty with the blocks organized by title.

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
            # Aqui eh realmente necessario pegar um eception generica
            # pylint: disable=broad-except
        except Exception as excpt:
            cls._log(excpt)
            return None

        boxes = cls.extract_text(file, block=True, norm=norm)
        first_title = False
        is_title = False
        actual_title = ''
        section = None

        for box in boxes:
            text = box[4].strip()
            is_title = True

            if text in ["SECAO I", "SECAO II", "SECAO III"]:
                if content_dict.get(section) or not section:
                    section = text
                if section not in content_dict.keys():
                    content_dict.update({section: {}})
                    actual_title = None
            else:
                for title in title_base:
                    text = text.replace("\n", " ")
                    title = title.replace("\n", " ")
                    normalized_title = cls._normalize_text(title, norm)

                    if text == normalized_title:
                        first_title = True
                        actual_title = normalized_title
                        if section and (title not in content_dict[section].keys()):
                            content_dict[section].update(
                                {normalized_title: []})
                    else:
                        is_title = False

            if first_title and not is_title and section and actual_title:
                if int(box[1]) != 55 and int(box[1]) != 881:
                    content_dict[section][actual_title].append(box[:5])

        return content_dict if not single else cls._save_single_file(file, 'json', json.dumps(content_dict))

    @classmethod
    def extract_to_txt(cls, folder='./', norm='NFKD'):
        """Extract information from DODF to a .txt file.

        For each PDF file in data/DODFs, the method extracts information from the
        PDF and writes it to the .txt file.

        Args:
            folder: The folder containing the PDFs to be extracted.
            norm: `Type of normalization <https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize>`_ applied to the text.

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
                with open(t_path, "w", encoding='utf-8') as file:
                    file.write(text)
            else:
                cls._log("TXT already exists")

    @classmethod
    def extract_to_json(cls, folder='./',
                        titles_with_boxes=False, norm='NFKD'):
        """Extract information from DODF to JSON.

        Args:
            folder: The folder containing the PDFs to be extracted.
            titles_with_boxes: If True, the method builds a dict containing a list of tuples (similar to `extract_structure`).
            Otherwise, the method structures a list of tuples (similar to `extract_text`).
            norm: `Type of normalization <https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize>`_ applied to the text.

        Returns:
            For each PDF file in data/DODFs, extract information from the
            PDF and output it to a JSON file.

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
                    with open(j_path, "w", encoding="utf-8") as file:
                        json.dump(content, file,
                                  ensure_ascii=False)
            else:
                cls._log("JSON already exists")

    @classmethod
    def _save_single_file(cls, file_path, file_type, content):
        file_path, _, _ = file_path.rpartition('.pdf')
        file_path = f"{file_path}.{file_type}"

        with open(file_path, 'w+', encoding='utf-8') as file:
            file.write(content)

    @classmethod
    def _normalize_text(cls, text, form='NFKD'):
        """This method is used for text nomalization.

        Args:
            text: The text to be normalized.
            form: `Type of normalization <https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize>`_ applied to the text.

        Returns:
            A string with the normalized text.

        """
        normalized = unicodedata.normalize(form, text).encode(
            'ascii', 'ignore').decode('utf8')
        return normalized

    @classmethod
    def _extract_titles(cls, file):
        """Extract titles and subtitles from the DODF.

        Args:
            file: The DODF to extract the titles.

        Returns:
            An object of type ExtractorTitleSubtitle, in which have the
            attributes:

            titles: get all titles from PDF.
            subtitle: get all subtitles from PDF.

        Raises:
            Exception: error in extracting titles from PDF.

        """
        try:
            title_database = ExtractorTitleSubtitle(file)
            cls._log(file)
        except Exception as exct:
            cls._log(f"Error in extracting files from {file}: {exct}")
            raise
        else:
            return title_database

    @classmethod
    def _get_pdfs_list(cls, folder):
        """Get DODFs list from the path.

        Args:
            folder: The folder containing the PDFs to be extracted.

        Returns:
            A list of DODFS' PDFs paths.

        """
        pdfs_path_list = []
        for dir_path, _, file_names in os.walk(os.path.expanduser(os.path.join(folder))):
            for file in file_names:
                if '.pdf' in file:
                    pdfs_path_list.append(os.path.join(dir_path, file))

        return pdfs_path_list

    @classmethod
    def _get_json_list(cls, folder):
        """Get list of exisiting JSONs from the path.

        Args:
            folder: The folder containing the PDFs to be extracted.

        Returns:
            A list of all exisiting JSONs.

        """
        aux = []
        for dir_path, _, file_names in os.walk(os.path.expanduser(os.path.join(folder, RESULTS_PATH_JSON))):
            for file in file_names:
                aux.append(os.path.join(dir_path, file))

        json_path_list = []
        for file in aux:
            json_path_list.append(os.path.splitext(os.path.basename(file))[0])

        return json_path_list

    @classmethod
    def _get_txt_list(cls, folder):
        """Get list of exisiting .txt files from the path.

        Args:
            folder: The folder containing the PDFs to be extracted.

        Returns:
            A list of all exisiting .txt files.

        """
        aux = []
        for dir_path, _, file_names in os.walk(os.path.expanduser(os.path.join(folder, RESULTS_PATH_TXT))):
            for file in file_names:
                aux.append(os.path.join(dir_path, file))

        txt_path_list = []
        for file in aux:
            txt_path_list.append(os.path.splitext(os.path.basename(file))[0])

        return txt_path_list

    @classmethod
    def _struct_subfolders(cls, path, json_f, folder):
        """Creates a directory for the JSON files.

        This method structures the folder tree for the allocation of
        files the code is curretly dealing with.

        Args:
            path: The path to the extracted file.
            json_f (boolean): If True, the file will extracted to a JSON. Otherwise, it will be extrated to a .txt.
            folder: The folder containing the PDFs to be extracted.

        Raises:
            FileExistsError: The folder being created is already there.

        Returns:
            The path created for the JSON to be saved.

        """
        type_f = '.json' if json_f else '.txt'
        res_path = RESULTS_PATH_JSON if json_f else RESULTS_PATH_TXT

        path = path.replace(folder, "", 1)
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

        This function might create a folder, observe if the folder already
        exists, or raise an error if the folder cannot be created.

        Args:
            path: The path to be created.

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
        """Print message from within the ContentExtractor class.

        Args:
            msg: String with message that should be printed out.
        """
        print(f"[EXTRACTOR] {msg}")
