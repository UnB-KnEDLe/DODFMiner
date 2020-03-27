from Extractor import ExtratorTituloSubTitulo
from flashtext import KeywordProcessor

from PIL import Image
import pytesseract
import os
import pdf2image
import time
import json
from difflib import SequenceMatcher
from pathlib import Path

TMP_PATH = "./data/tmp/"
TMP_PATH_IMAGES = "./data/tmp/images"
TMP_PATH_JSON = "./data/tmp/json"

class ContentExtractor:

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
        try:
            ext = ExtratorTituloSubTitulo(file)
            print(file)
        except Exception as e:
            print("Erro na extração de titulos do pdf: " + file)
            print(e)
            raise
        else:
            return ext

    @classmethod
    def _convert_image(cls, file):
        return pdf2image.convert_from_path(file,
                                           dpi=200,
                                           fmt='jpg',
                                           thread_count=8,
                                           use_cropbox=False,
                                           strict=False)

    @classmethod
    def _save_images(cls, images_array):
        for i, im in enumerate(images_array):
            im.save((TMP_PATH_IMAGES + "/tmp_image_{}.jpg").format(i))

    @classmethod
    def _sort_images(cls):
        return sorted(os.listdir(TMP_PATH_IMAGES),
                      key=lambda x: int(x.split("_")[2].split('.')[0]))

    @classmethod
    def _tesseract_processing(cls):
        tesseract_result = ''
        sorted_images = cls._sort_images()
        for image in sorted_images:
            image_r = Image.open(os.path.join(TMP_PATH_IMAGES, image))
            inicio = time.time()
            text = pytesseract.image_to_string(image_r,
                                               config='--oem 1',
                                               lang='por')
            fim = time.time()
            print(image + " Tempo: " + str(fim-inicio))
            tesseract_result += text

        return tesseract_result

    @classmethod
    def _write_tesseract_text(cls, text):
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
        pdfs_path_list = []
        for dp, dn, fn in os.walk(os.path.expanduser('./data/dodfs')):
            for f in fn:
                pdfs_path_list.append(os.path.join(dp, f))

        return pdfs_path_list

    @classmethod
    def _get_json_list(cls):
        aux = []
        for dp, dn, fn in os.walk(os.path.expanduser(TMP_PATH_JSON)):
            for f in fn:
                aux.append(os.path.join(dp, f))

        json_path_list = []
        for file in aux:
            json_path_list.append(os.path.splitext(os.path.basename(file))[0])

        return json_path_list

    @classmethod
    def _create_json_folder(cls, path):
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
            print('Pasta já criada')
        return final_path

    @classmethod
    def _remove_images(cls):
        for file in os.listdir(TMP_PATH_IMAGES):
            try:
                os.remove(os.path.join(TMP_PATH_IMAGES, file))
            except Exception as e:
                print("Failed with:", e.strerror)
                print("Error code:", e.code)

    @classmethod
    def extract_content(cls, file):
        cls._remove_images()
        try:
            ext = cls._extract_titles(file)
        except Exception as e:
            print(e)
        else:
            pil_images = cls._convert_image(file)
            cls._save_images(pil_images)
            tesseract_result = cls._tesseract_processing()
            tesseract_result = open(TMP_PATH + 'tmp_tesseract_text.txt', 'r').read()
            cls._write_tesseract_text(tesseract_result)
            terms_found = cls._process_text(tesseract_result, ext.json)
            content_dict = cls._extract_content(tesseract_result, terms_found, ext)
            j_path = cls._create_json_folder(file)
            json.dump(content_dict, open(TMP_PATH_JSON + '/' + j_path, "w",
                                         encoding="utf-8"))

    @classmethod
    def extract_to_json(cls):
        pdfs_path_list = cls._get_pdfs_list()
        json_path_list = cls._get_json_list()

        print(pdfs_path_list)
        for file in pdfs_path_list:
            pdf_name = os.path.splitext(os.path.basename(file))[0]
            if pdf_name not in json_path_list:
                if os.path.getsize(file) < 30000000:
                    cls.extract_content(file)
            else:
                print("json já existe")
