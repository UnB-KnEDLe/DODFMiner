import os
import unicodedata
import json
import shutil

from glob import glob
from dodfminer.extract.pure.core import ContentExtractor

def test_pure_extract_text_single():
    file = ""+os.path.dirname(__file__)+"/support/dodfminer_sf.pdf"
    generated_txt = "BRASILIA - DF, QUINTA-FEIRA, 2 DE JANEIRO DE 2020 SECAO I SUMARIO"
    ContentExtractor.extract_text(file, single=True)
    assert os.path.isfile(file.replace("pdf", "txt"))
    assert generated_txt in open(file.replace("pdf", "txt")).read()
    os.remove(file.replace("pdf", "txt"))

def test_pure_extract_text_return_text():
    file = ""+os.path.dirname(__file__)+"/support/dodfminer_sf.pdf"
    generated_txt = "BRASILIA - DF, QUINTA-FEIRA, 2 DE JANEIRO DE 2020 SECAO I SUMARIO"
    assert generated_txt in ContentExtractor.extract_text(file)

def test_pure_extract_text_return_list():
    file = ""+os.path.dirname(__file__)+"/support/dodfminer_sf.pdf"
    generated_txt = "BRASILIA - DF, QUINTA-FEIRA, 2 DE JANEIRO DE 2020 SECAO I SUMARIO"
    assert len(ContentExtractor.extract_text(file, block=True)) > 0

def test_pure_extract_text_single_return_list():
    file = ""+os.path.dirname(__file__)+"/support/dodfminer_sf.pdf"
    generated_txt = "BRASILIA - DF, QUINTA-FEIRA, 2 DE JANEIRO DE 2020 SECAO I SUMARIO"
    ContentExtractor.extract_text(file, single=True, block=True)
    assert os.path.isfile(file.replace("pdf", "json"))
    assert len(json.loads(open(file.replace('pdf', 'json')).read())) > 0
    os.remove(file.replace("pdf", "json"))

# def test_pure_extract_text_norm():
#     file = ""+os.path.dirname(__file__)+"/support/dodfminer_sf.pdf"
#     generated_txt = "BRASILIA - DF, QUINTA-FEIRA, 2 DE JANEIRO DE 2020 SECAO I SUMARIO"
#     assert unicodedata.is_normalized("NFC", ContentExtractor.extract_text(file, norm="NFC"))

def test_pure_extract_structure_single():
    file = ""+os.path.dirname(__file__)+"/support/dodfminer_sf.pdf"
    ContentExtractor.extract_structure(file, single=True)
    assert os.path.isfile(file.replace("pdf", "json"))
    assert 'PODER EXECUTIVO' in json.loads(open(file.replace("pdf", "json")).read()).keys()
    os.remove(file.replace("pdf", "json"))

def test_pure_extract_structure():
    file = ""+os.path.dirname(__file__)+"/support/dodfminer_sf.pdf"
    assert 'PODER EXECUTIVO' in ContentExtractor.extract_structure(file).keys()

def test_pure_extract_to_txt():
    folder = ""+os.path.dirname(__file__)+"/support/dodf_pdfs"
    res_folder = folder + '/results/txt/2020/01_Janeiro/'
    ContentExtractor.extract_to_txt(folder)
    assert os.path.isdir(res_folder)
    assert len(glob(res_folder+'*.txt')) > 1

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
    res_folder = folder + '/results/json/2020/01_Janeiro/'
    ContentExtractor.extract_to_json(folder, titles_with_boxes=True)
    ContentExtractor.extract_to_json(folder, titles_with_boxes=True)
    captured = capsys.readouterr()
    assert "JSON already exists" in captured.out
    shutil.rmtree(folder + '/results/')

def test_pure_extract_to_txt_already_exists(capsys):
    folder = ""+os.path.dirname(__file__)+"/support/dodf_pdfs"
    res_folder = folder + '/results/txt/2020/01_Janeiro/'
    ContentExtractor.extract_to_txt(folder)
    ContentExtractor.extract_to_txt(folder)
    captured = capsys.readouterr()
    assert "TXT already exists" in captured.out
    shutil.rmtree(folder + '/results/')
