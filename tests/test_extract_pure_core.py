import os
import json
import shutil

from glob import glob
from dodfminer.extract.pure.core import ContentExtractor

EXPECTED_EXTRACTED_TEXT = "BRASILIA - DF, QUINTA-FEIRA, 2 DE JANEIRO DE 2020"
DODF_FILE_PATH = file = "" + \
    os.path.dirname(__file__)+"/support/dodfminer_sf.pdf"


def test_pure_extract_text_single():
    txt_file_path = DODF_FILE_PATH.replace("pdf", "txt")

    ContentExtractor.extract_text(DODF_FILE_PATH, single=True)

    assert os.path.isfile(txt_file_path)
    with open(txt_file_path, encoding='utf-8') as txt_file:
        assert EXPECTED_EXTRACTED_TEXT in txt_file.read()

    os.remove(txt_file_path)


def test_pure_extract_text_return_text():
    assert EXPECTED_EXTRACTED_TEXT in ContentExtractor.extract_text(
        DODF_FILE_PATH)


def test_pure_extract_text_return_list():
    file_pdf = ""+os.path.dirname(__file__)+"/support/dodfminer_sf.pdf"
    # generated_txt = "BRASILIA - DF, QUINTA-FEIRA, 2 DE JANEIRO DE 2020 SECAO I SUMARIO"
    assert len(ContentExtractor.extract_text(file_pdf, block=True)) > 0


def test_pure_extract_text_single_return_list():
    json_file_path = DODF_FILE_PATH.replace("pdf", "json")

    ContentExtractor.extract_text(DODF_FILE_PATH, single=True, block=True)

    assert os.path.isfile(json_file_path)
    with open(json_file_path, encoding='utf-8') as json_file:
        assert len(json.loads(json_file.read())) > 0

    os.remove(json_file_path)


def test_pure_extract_text_json_false_saves_txt_file():
    txt_file_path = DODF_FILE_PATH.replace("pdf", "txt")

    ContentExtractor.extract_text(
        DODF_FILE_PATH, single=True, block=True, is_json=False)

    assert os.path.isfile(txt_file_path)
    with open(txt_file_path, encoding='utf-8') as txt_file:
        content = txt_file.read()
        assert isinstance(content, str)
        assert len(content) > 0

    os.remove(txt_file_path)


# def test_pure_extract_text_norm():
#     file = ""+os.path.dirname(__file__)+"/support/dodfminer_sf.pdf"
#     generated_txt = "BRASILIA - DF, QUINTA-FEIRA, 2 DE JANEIRO DE 2020 SECAO I SUMARIO"
#     assert unicodedata.is_normalized("NFC", ContentExtractor.extract_text(file, norm="NFC"))


def test_pure_extract_structure_single():
    pdf_file = ""+os.path.dirname(__file__)+"/support/dodfminer_sf.pdf"
    json_file = pdf_file.replace("pdf", "json")

    ContentExtractor.extract_structure(pdf_file, single=True)

    assert os.path.isfile(json_file)

    with open(json_file, encoding='utf-8') as file_pointer:
        file_content = file_pointer.read()
        assert 'SECAO I' in json.loads(file_content).keys()
        assert 'PODER EXECUTIVO' in json.loads(file_content)['SECAO I'].keys()

    os.remove(file.replace("pdf", "json"))

def test_pure_extract_structure():
    pdf_file = ""+os.path.dirname(__file__)+"/support/dodfminer_sf.pdf"

    assert 'SECAO I' in ContentExtractor.extract_structure(pdf_file)
    assert 'PODER EXECUTIVO' in ContentExtractor.extract_structure(pdf_file)['SECAO I']

def test_pure_extract_structure_key_correcteness():
    pdf_file = ""+os.path.dirname(__file__)+"/support/dodf_pdfs/2020/01_Janeiro/DODF 003 21-01-2020 EDICAO EXTRA.pdf"
    structure = ContentExtractor.extract_structure(pdf_file)

    assert 'SECAO II' in structure
    assert 'PODER EXECUTIVO' in structure['SECAO II']
    assert 'SECAO III' in structure
    assert 'SECRETARIA DE ESTADO DO ESPORTE E LAZER' in structure['SECAO III']

def test_pure_extract_to_txt():
    folder = ""+os.path.dirname(__file__)+"/support/dodf_pdfs"
    res_folder = folder + '/results/txt/2020/01_Janeiro/'
    ContentExtractor.extract_to_txt(folder)
    assert os.path.isdir(res_folder)
    assert len(glob(res_folder+'*.txt')) > 1
    shutil.rmtree(folder + '/results/')


def test_pure_extract_to_json_without_titles():
    folder = ""+os.path.dirname(__file__)+"/support/dodf_pdfs"
    res_folder = folder + '/results/json/2020/01_Janeiro/'
    ContentExtractor.extract_to_json(folder)
    assert os.path.isdir(res_folder)
    assert len(glob(res_folder+'*.json')) > 1
    shutil.rmtree(folder + '/results/')


def test_pure_extract_to_json_with_titles():
    folder = ""+os.path.dirname(__file__)+"/support/dodf_pdfs"
    res_folder = folder + '/results/json/2020/01_Janeiro/'
    ContentExtractor.extract_to_json(folder, titles_with_boxes=True)
    assert os.path.isdir(res_folder)
    assert len(glob(res_folder+'*.json')) > 1
    shutil.rmtree(folder + '/results/')


def test_pure_extract_to_json_already_exists(capsys):
    folder = ""+os.path.dirname(__file__)+"/support/dodf_pdfs"
    # res_folder = folder + '/results/json/2020/01_Janeiro/'
    ContentExtractor.extract_to_json(folder, titles_with_boxes=True)
    ContentExtractor.extract_to_json(folder, titles_with_boxes=True)
    captured = capsys.readouterr()
    assert "JSON already exists" in captured.out
    shutil.rmtree(folder + '/results/')


def test_pure_extract_to_txt_already_exists(capsys):
    folder = ""+os.path.dirname(__file__)+"/support/dodf_pdfs"
    # res_folder = folder + '/results/txt/2020/01_Janeiro/'
    ContentExtractor.extract_to_txt(folder)
    ContentExtractor.extract_to_txt(folder)
    captured = capsys.readouterr()
    assert "TXT already exists" in captured.out
    shutil.rmtree(folder + '/results/')

# pylint: disable=protected-access
def test_pure_struct_subfolders_in_current_folder():
    folder = "." # test case with . signature meaning current folder
    path = "./DODF 011 16-01-2019.pdf"

    txt_path = ContentExtractor._struct_subfolders(path, False, folder)
    assert txt_path == "./results/txt/DODF 011 16-01-2019.txt"
