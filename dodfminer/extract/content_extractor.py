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
import pdf2image
import pytesseract
import fitz
import unicodedata


from PIL import Image
from pathlib import Path
from difflib import SequenceMatcher
from flashtext import KeywordProcessor
from fuzzysearch import find_near_matches

from cli import GLOBAL_ARGS
from extract.spellcheck import SpellChecker
from prextract.title_extractor import ExtractorTitleSubtitle
from prextract.box_extractor import get_doc_text_boxes

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
    def extract_content(cls, file, extract_backend,
                        pure_text=False,
                        titles_with_boxes=False,
                        callback=[]):
        """Extract content from a pdf file to JSON.

        Args:
            file: The DODF pdf file to extract the content
            callback: A list of callbacks to modify the Tesseract output
            tmp_folder
        Raises:
            Exception: Error in case of the title/subtitle pre-extractions
            fails

        Returns:
            Return a dictionary with titles and subtitles and your contents

        """
        print(titles_with_boxes)
        try:
            # Gather all the titles and sub from the dodf to be extracted
            # The titles are used as a database of keys, so the tesseract
            # can easly find all the sections desired
            title_base = cls._extract_titles(file)
        except Exception as e:
            cls._log(f"Exception error: {e}")
        else:
            if titles_with_boxes:
                return cls._extract_boxes_with_title(file)
            elif extract_backend == 'tesseract':
                text_extracted = cls._tesseract_extraction(file, title_base, callback)
            elif extract_backend == 'drawboxes':
                text_extracted = cls._drawboxes_extraction(file)
            if not pure_text and not titles_with_boxes:
                try:
                    terms_found = cls._process_text(text_extracted, title_base.json)
                    # Populate a dictionary with title and subtitle as keys and
                    # the content as value
                    content_dict = cls._extract_content(text_extracted,
                                                        terms_found, title_base.json)
                except Exception as e:
                    cls._log(f"Exception error: {e}")
                    raise
                else:
                    return content_dict
            else:
                return text_extracted

    @classmethod
    def extract_to_txt(cls, extract_backend):
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
                text = cls.extract_content(file, extract_backend, True)
                t_path = cls._struct_txt_subfolders(file)
                text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf8')
                f = open(RESULTS_PATH_TXT + '/' + t_path, "w")
                f.write(text)
            else:
                cls._log("TXT already exists")

    @classmethod
    def extract_to_json(cls, extract_backend, titles_with_boxes=False):
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

        callback = []
        callback_name = GLOBAL_ARGS.cb_type
        if callback_name == 'spellcheck':
            callback.append(SpellChecker().text_correction)

        for file in pdfs_path_list:
            pdf_name = os.path.splitext(os.path.basename(file))[0]
            # We do not want the system to repeat itself doing the same work
            if pdf_name not in json_path_list:
                # TODO(Khalil009) Include a CLI Flag to make only
                # low cost extractions
                if os.path.getsize(file) < 30000000:  # Remove in future.
                    # Remove images that might still there from previous exec
                    # cls._remove_images()
                    content_dict = cls.extract_content(file, extract_backend, titles_with_boxes=titles_with_boxes, callback=[])
                    j_path = cls._struct_json_subfolders(file)
                    json.dump(content_dict, open(RESULTS_PATH_JSON + '/' + j_path, "w",
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
            boxes = cls._textboxes(file)
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
    def _textboxes(cls, file):
        list_of_boxes = []
        pymu_file = fitz.open(file)
        for textboxes in get_doc_text_boxes(pymu_file):
            for text in textboxes:
                list_of_boxes.append(text)
                
        return list_of_boxes

    @classmethod
    def _drawboxes_extraction(cls, file):
        drawboxes_text = ''
        pymu_file = fitz.open(file)
        for textboxes in get_doc_text_boxes(pymu_file):
            for text in textboxes:
                if int(text[1]) != 55 and int(text[1]) != 881:
                    drawboxes_text += (text[4] + ' ')

        return drawboxes_text

    @classmethod
    def _tesseract_extraction(cls, file, title_base, callback):
        # The tesseract library does not work with pdfs, for that the
        # DODF is converted in between multiple lines
        pil_images = cls._convert_image(file)
        # cls._save_images(pil_images)
        # Calls Tesseract Backend to process the image and convert to text
        # TODO: This sould be allowed in to change in future versions
        tesseract_result = cls._tesseract_processing(pil_images, callback)
        # Write on file to logc
        # Only foe debbuging
        # cls._write_tesseract_text(tesseract_result)
        # List all titles found through the role text
        return tesseract_result

    # @classmethod
    # def _process_text(cls, text, titles):
    #     """Search through the text the titles and subtitles.
    #
    #     This function uses a library called flashtext which is responsible
    #     to search through the text for titles and subtitles from the database.
    #     In this function will be placed the title rules.
    #
    #     Args:
    #         text: The full dodf text as string.
    #         titles: An json property from ExtractorTitleSubtitle object.
    #
    #     Returns:
    #         A list of keywords to be searched through text with the tuple
    #         format of (keyword, start, end). Where start and end are indexes
    #         of the full string.
    #
    #     """
    #     keyword_processor = KeywordProcessor(case_sensitive=True)
    #     titles_list = [key for key in titles.keys()]
    #     import pdb; pdb.set_trace()
    #     for title in titles_list:
    #         keyword_processor.add_keyword('\n'+title+'\n')
    #         keyword_processor.add_keyword('\n'+title+' Í\n')
    #
    #     # The extract keywords return an array of tupples (keyword, start, end)
    #     # Where the keyword is the title, and the start and end is the indexes
    #     # of the string, where the keyword is contained
    #     keywords = keyword_processor.extract_keywords(text, span_info=True)
    #     # This last keyword is added to indicate the the last title is
    #     # non existent
    #     keywords.append(("", len(text), None))
    #
    #     return keywords

    @classmethod
    def _process_text(cls, text, titles):
        """Search through the text the titles and subtitles.

        This function uses a library called flashtext which is responsible
        to search through the text for titles and subtitles from the database.
        In this function will be placed the title rules.

        Args:
            text: The full dodf text as string.
            titles: An json property from ExtractorTitleSubtitle object.

        Returns:
            A list of keywords to be searched through text with the tuple
            format of (keyword, start, end). Where start and end are indexes
            of the full string.

        """
        titles_list = [key for key in titles.keys()]
        keywords = []
        for title in titles_list:
            matches = find_near_matches('\n'+title+'\n', text, max_l_dist=1)
            for match in matches:
                keywords.append((match.matched, match.start, match.end))
        # The extract keywords return an array of tupples (keyword, start, end)
        # Where the keyword is the title, and the start and end is the indexes
        # of the string, where the keyword is contained
        # This last keyword is added to indicate the the last title is
        # non existent
        keywords.append(("", len(text), None))

        return keywords

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
        return pdf2image.convert_from_path(file, dpi=200,
                                           fmt='jpg',
                                           thread_count=8, strict=False,
                                           use_cropbox=False)

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
    def _tesseract_processing(cls, images, callback=None):
        """Use tesseract to extract content from images.

        Returns:
            The whole pdf file in a single string

        """
        tesseract_result = ''
        # Images in directory would be read by alphabetical order. In which
        # would cause page 11 to be processed before page 2. For that, the
        # images are sorted through page number.
        # sorted_images = cls._sort_images()
        sorted_images = images
        for i, image in enumerate(images):
            # image_r = Image.open(os.path.join(TMP_PATH_IMAGES, image))
            # Time is used only for profiling purposes
            start = time.time()
            # Convert the image to strinc using tesseract
            # TODO: Configs should be passed through CLI
            text = pytesseract.image_to_string(image,
                                               config='--oem 1',
                                               lang='por')
            end = time.time()
            cls._log('Page ' + str(i+1) + " Time: " + str(end-start))
            tesseract_result += text

        # TODO: Return string from section, index with title and subtitle
        # go to next string
        if callback:
            try:
                for method in callback:
                    tesseract_result = method(tesseract_result)
            except:
                error = "Callback must be a function with one str parameter"
                raise Exception(error)

        return tesseract_result

    @classmethod
    def _write_tesseract_text(cls, text):
        """Write tesseract text to a temporary file.

        Args:
            text: The text to be written.

        """
        text_file = open(TMP_PATH + "tmp_tesseract_text.txt", "w")
        text_file.write(text.encode('utf8'))

    @classmethod
    def _extract_content(cls, text, terms_found, ext):
        """Populate a dict with the dodf content.

        The dictionary have the title as key and the content as value.

        Args:
            text: The whole DODF pdf text as string
            terms_found: the titles and subtitles found in the txt
            ext: all titles and subtitles from the base

        Returns:
            Dictionary where the key is a title and the description
            its content

        """
        content_dict = {}
        for i in range(len(terms_found)-1):
            interval_text = text[terms_found[i][2]+1:terms_found[i+1][1]]
            for key in ext.keys():
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
