"""."""

import os
import time
import json
import pdf2image
import pytesseract

from PIL import Image
from pathlib import Path
from difflib import SequenceMatcher
from flashtext import KeywordProcessor

from prextract.title_extractor import ExtractorTitleSubtitle

TMP_PATH = "./data/tmp/"
TMP_PATH_IMAGES = "./data/tmp/images"
TMP_PATH_JSON = "./data/tmp/json"


class ContentExtractor:
    """."""

    @classmethod
    def _process_text(cls, text, titles):
        keyword_processor = KeywordProcessor(case_sensitive=True)
        titles_list = [key for key in titles.keys()]
        for title in titles_list:
            keyword_processor.add_keyword('\n'+title+'\n')
            keyword_processor.add_keyword('\n'+title+' Í\n')

        found = keyword_processor.extract_keywords(text, span_info=True)
        found.append(("", len(text), None))

        return found

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
    def _convert_image(cls, file):
        """Convert pdf file to images.

        Each pdf page will turn into a single image.

        Args:
            file: The DODF pdf to convert in images

        Returns:
            A list of images in memory, each image is one page of the pdf.

        """
        # TODO: Use CLI to choose this parameters
        return pdf2image.convert_from_path(file, dpi=200, fmt='jpg',
                                           thread_count=8, use_cropbox=False,
                                           strict=False)

    @classmethod
    def _save_images(cls, images_array):
        """Save images to disk at data/tmp/img.

        Args:
            images_array: An array of images in memory.

        """
        for i, im in enumerate(images_array):
            im.save((TMP_PATH_IMAGES + "/tmp_image_{}.jpg").format(i))

    @classmethod
    def _sort_images(cls):
        """Sort images by page number.

        Returns:
            Vector of image paths and names sorted by number.

        """
        return sorted(os.listdir(TMP_PATH_IMAGES),
                      key=lambda x: int(x.split("_")[2].split('.')[0]))

    @classmethod
    def _tesseract_processing(cls):
        """Use tesseract to extract content from images.

        Returns:
            The whole pdf file in a single string

        """
        tesseract_result = ''
        # Images in directory would be read by alphabetical order. In which
        # would cause page 11 to be processed before page 2. For that, the
        # images are sorted through page number.
        sorted_images = cls._sort_images()
        for image in sorted_images:
            image_r = Image.open(os.path.join(TMP_PATH_IMAGES, image))
            # Time is used only for profiling purposes
            start = time.time()
            # Convert the image to strinc using tesseract
            # TODO: Configs should be passed through CLI
            text = pytesseract.image_to_string(image_r,
                                               config='--oem 1',
                                               lang='por')
            end = time.time()
            cls._log(image + " Tempo: " + str(end-start))
            tesseract_result += text

        # TODO: Return string from section, index with title and subtitle
        # go to next string
        return tesseract_result

    @classmethod
    def _write_tesseract_text(cls, text):
        """Write tesseract text to a temporary file.

        Args:
            text: The text to be written.

        """
        text_file = open(TMP_PATH + "tmp_tesseract_text.txt", "w")
        text_file.write(text)

    @classmethod
    def _extract_content(cls, text, terms_found, ext):
        content_dict = {}

        for i in range(len(terms_found)-1):
            interval_text = text[terms_found[i][2]+1:terms_found[i+1][1]]
            for key in ext.json.keys():
                if SequenceMatcher(None, key, terms_found[i][0]).ratio() > 0.8:
                    if key in content_dict:
                        content_dict[key].append(interval_text)
                    else:
                        content_dict[key] = [interval_text]

        return content_dict

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
        for dp, _, fn in os.walk(os.path.expanduser(TMP_PATH_JSON)):
            for f in fn:
                aux.append(os.path.join(dp, f))

        json_path_list = []
        for file in aux:
            json_path_list.append(os.path.splitext(os.path.basename(file))[0])

        return json_path_list

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
        path = Path(TMP_PATH_JSON + '/' + '/'.join(splited[:-1]))
        try:
            path.mkdir(parents=True)
        except FileExistsError as e:
            cls._log(f'Folder Already Exist: {e}')

        return final_path

    @classmethod
    def _remove_images(cls):
        """Remove tesseract images from temporary directory.

        Raises:
            Exception: Some fail to remove the image.

        """
        for file in os.listdir(TMP_PATH_IMAGES):
            try:
                os.remove(os.path.join(TMP_PATH_IMAGES, file))
            except Exception as e:
                cls._log("Failed with:", e.strerror)
                cls._log("Error code:", e.code)

    @classmethod
    def extract_content(cls, file):
        """.

        Args:
            file: The DODF pdf file to extract the content

        Raises:
            Exception: Error in case of the title/subtitle pre-extractions
            fails

        """
        # Remove images that might still there from previous exec
        cls._remove_images()
        try:
            # Gather all the titles and sub from the dodf to be extracted
            # The titles are used as a database of keys, so the tesseract
            # can easly find all the sections desired
            ext = cls._extract_titles(file)
        except Exception as e:
            cls._log(f"Exception error: {e}")
        else:
            # The tesseract library does not work with pdfs, for that the
            # DODF is converted in between multiple lines
            pil_images = cls._convert_image(file)
            cls._save_images(pil_images)
            # Calls Tesseract Backend to process the image and convert to text
            # TODO: This sould be allowed in to change in future versions
            tesseract_result = cls._tesseract_processing()
            tesseract_result = open(TMP_PATH
                                    + 'tmp_tesseract_text.txt', 'r').read()
            # Escrever algo aqui
            cls._write_tesseract_text(tesseract_result)
            terms_found = cls._process_text(tesseract_result, ext.json)
            content_dict = cls._extract_content(tesseract_result,
                                                terms_found, ext)
            j_path = cls._struct_json_subfolders(file)
            json.dump(content_dict, open(TMP_PATH_JSON + '/' + j_path, "w",
                                         encoding="utf-8"))

    @classmethod
    def extract_to_json(cls):
        """Extract information from DODF to JSON.

        For each pdf file in data/dodfs, extract information from the
        pdf and output it to json.

        """
        # Get list of all downloaded pdfs
        pdfs_path_list = cls._get_pdfs_list()
        # Get list of existing json to not repeat work
        json_path_list = cls._get_json_list()

        cls._log(pdfs_path_list)
        for file in pdfs_path_list:
            pdf_name = os.path.splitext(os.path.basename(file))[0]
            # We do not want the system to repeat itself doing the same work
            if pdf_name not in json_path_list:
                # TODO(Khalil009) Include a CLI Flag to make only
                # low cost extractions
                if os.path.getsize(file) < 30000000:  # Remove in future.
                    cls.extract_content(file)
            else:
                cls._log("JSON already exists")

    @classmethod
    def _log(cls, msg):
        print(f"[EXTRACTOR] {msg}")
