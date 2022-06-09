import os
import json
import sys
from glob import glob
import shutil
from unittest.mock import patch
import pytest
from dodfminer.run import run
from dodfminer.extract.polished.core import _acts_ids

EMPTY_ARGS_MSG = """usage: DODFMiner [-h] {downloader,extract} ...

Data extractor of PDF documents from the Official Gazette of the Federal
District, Brazil.

positional arguments:
  {downloader,extract}

optional arguments:
  -h, --help            show this help message and exit

© Copyright 2020, KnEDLe Team. Version 1.1.3.4
"""

ONLY_EXTRACTED_MSG = "usage: DODFMiner extract"

act_choices = list(_acts_ids.keys())


def test_run_no_args():
    with pytest.raises(SystemExit):
        with patch.object(sys, 'argv', ['cmd', '']):
            run()


def test_run_only_extract_arg(capsys):
    targets = ['cmd', 'extract']
    with patch.object(sys, 'argv', targets):
        run()
        captured = capsys.readouterr()
        assert ONLY_EXTRACTED_MSG in captured.out


def test_run_extract_single_file_pure_text():
    file = ""+os.path.dirname(__file__)+"/support/dodfminer_sf.pdf"
    targets = ["cmd", "extract", "-s", file, "-t", "pure-text"]
    content_txt = "NOMEAR JOSE ANTONIO BARBOSA, Tecnico de Gestao Educacional,"
    with patch.object(sys, 'argv', targets):
        run()
        assert os.path.exists(file.replace('pdf', 'txt'))
        with open(file.replace('pdf', 'txt'), encoding='utf-8') as file_txt:
            assert content_txt in file_txt.read()
        os.remove(file.replace('pdf', 'txt'))


def test_run_extract_single_file_with_titles():
    file = "" + os.path.dirname(__file__) + "/support/dodfminer_sf.pdf"
    targets = ["cmd", "extract", "-s", file, "-t", "with-titles"]

    with patch.object(sys, 'argv', targets):
        run()

        assert os.path.exists(file.replace('pdf', 'json'))

        with open(file.replace('pdf', 'json'), encoding='utf-8') as json_pointer:
            json_file = json_pointer.read()
            res_dict = json.loads(json_file)

        assert "SECAO I" in res_dict.keys()
        assert "PODER EXECUTIVO" in res_dict['SECAO I'].keys()

        os.remove(file.replace('pdf', 'json'))


def test_run_extract_single_file_blocks():
    file = ""+os.path.dirname(__file__)+"/support/dodfminer_sf.pdf"
    targets = ["cmd", "extract", "-s", file, "-t", "blocks"]
    with patch.object(sys, 'argv', targets):
        run()
        assert os.path.exists(file.replace('pdf', 'json'))
        with open(file.replace('pdf', 'json'), encoding='utf-8') as json_file:
            res_dict = json.loads(json_file.read())
            assert len(res_dict) > 0
        os.remove(file.replace('pdf', 'json'))


def test_run_extract_single_all_act():
    folder = ""+os.path.dirname(__file__)+"/support/"
    file = folder+"dodfminer_sf.pdf"
    targets = ["cmd", "extract", "-s", file, "-a"]
    with patch.object(sys, 'argv', targets):
        run()
        for act in act_choices:
            assert os.path.isfile(folder+act+".csv")
            os.remove(folder+act+".csv")


def test_run_extract_single_all_act_parallel():
    folder = ""+os.path.dirname(__file__)+"/support/"
    file = folder+"dodfminer_sf.pdf"
    targets = ["cmd", "extract", "-s", file, "-a", "-p", "4"]
    with patch.object(sys, 'argv', targets):
        run()
        for act in act_choices:
            assert os.path.isfile(folder+act+".csv")
            os.remove(folder+act+".csv")


def test_run_extract_input_folder_pure_text():
    folder = ""+os.path.dirname(__file__)+"/support/dodf_pdfs"
    targets = ["cmd", "extract", "-i", folder, "-t", "pure-text"]
    with patch.object(sys, 'argv', targets):
        run()
        res_folder = folder + '/results/txt/2020/01_Janeiro/'
        assert os.path.isdir(res_folder)
        assert len(glob(res_folder+'*.txt')) > 1
        shutil.rmtree(folder + '/results/')


def test_run_extract_input_folder_with_titles():
    folder = ""+os.path.dirname(__file__)+"/support/dodf_pdfs"
    targets = ["cmd", "extract", "-i", folder, "-t", "with-titles"]
    with patch.object(sys, 'argv', targets):
        run()
        res_folder = folder + '/results/json/2020/01_Janeiro/'
        assert os.path.isdir(res_folder)
        assert len(glob(res_folder+'*.json')) > 1
        shutil.rmtree(folder + '/results/')


def test_run_extract_input_folder_one_act():
    folder = ""+os.path.dirname(__file__)+"/support/dodf_pdfs"
    targets = ["cmd", "extract", "-i", folder, "-a", "aposentadoria"]
    with patch.object(sys, 'argv', targets):
        run()
        assert os.path.isfile(folder+"/aposentadoria.csv")
        os.remove(folder+"/aposentadoria.csv")


def test_run_extract_input_folder_one_act_parallel():
    folder = ""+os.path.dirname(__file__)+"/support/dodf_pdfs"
    targets = ["cmd", "extract", "-i", folder,
               "-a", "aposentadoria", "-p", "4"]
    with patch.object(sys, 'argv', targets):
        run()
        assert os.path.isfile(folder+"/aposentadoria.csv")
        os.remove(folder+"/aposentadoria.csv")


def test_run_extract_input_folder_two_act():
    folder = ""+os.path.dirname(__file__)+"/support/dodf_pdfs"
    targets = ["cmd", "extract", "-i", folder, "-a", "aposentadoria", "abono"]

    with patch.object(sys, 'argv', targets):
        run()

        assert os.path.isfile(folder+"/aposentadoria.csv")
        assert os.path.isfile(folder+"/abono.csv")

        os.remove(folder+"/aposentadoria.csv")
        os.remove(folder+"/abono.csv")


def test_run_extract_input_folder_two_act_parallel():
    folder = ""+os.path.dirname(__file__)+"/support/dodf_pdfs"
    targets = ["cmd", "extract", "-i", folder,
               "-a", "aposentadoria", "abono", "-p", "4"]

    with patch.object(sys, 'argv', targets):
        run()

        assert os.path.isfile(folder+"/aposentadoria.csv")
        assert os.path.isfile(folder+"/abono.csv")

        os.remove(folder+"/aposentadoria.csv")
        os.remove(folder+"/abono.csv")


def test_run_extract_input_folder_all_act():
    folder = ""+os.path.dirname(__file__)+"/support/dodf_pdfs/"
    targets = ["cmd", "extract", "-i", folder, "-a"]
    with patch.object(sys, 'argv', targets):
        run()
        for act in act_choices:
            assert os.path.isfile(folder+act+".csv")
            os.remove(folder+act+".csv")
    # shutil.rmtree(folder + '/results')


def test_run_extract_input_folder_all_act_parallel():
    folder = ""+os.path.dirname(__file__)+"/support/dodf_pdfs/"
    targets = ["cmd", "extract", "-i", folder, "-a", "-p", "4"]
    with patch.object(sys, 'argv', targets):
        run()
        for act in act_choices:
            assert os.path.isfile(folder+act+".csv")
            os.remove(folder+act+".csv")
    shutil.rmtree(folder + '/results')


def test_run_extract_input_folder_one_act_back_end_ner():
    folder = ""+os.path.dirname(__file__)+"/support/dodf_pdfs"
    targets = ["cmd", "extract", "-i", folder,
               "-a", "aposentadoria", "-b", "ner"]
    with patch.object(sys, 'argv', targets):
        run()
        assert os.path.isfile(folder+"/aposentadoria.csv")
        os.remove(folder+"/aposentadoria.csv")


def test_run_extract_input_folder_one_act_back_end_ner_parallel():
    folder = ""+os.path.dirname(__file__)+"/support/dodf_pdfs"
    targets = ["cmd", "extract", "-i", folder,
               "-a", "aposentadoria", "-b", "ner", "-p", "4"]
    with patch.object(sys, 'argv', targets):
        run()
        assert os.path.isfile(folder+"/aposentadoria.csv")
        os.remove(folder+"/aposentadoria.csv")


def test_run_extract_single_file_committee_classification():
    folder = ""+os.path.dirname(__file__)+"/support/"
    file = folder+"dodfminer_sf.pdf"
    targets = ["cmd", "extract", "-s", file, "-a", "-c"]
    with patch.object(sys, 'argv', targets):
        run()
        for act in act_choices:
            assert os.path.isfile(folder+act+".csv")
            os.remove(folder+act+".csv")


def test_run_extract_input_folder_committee_classification():
    folder = ""+os.path.dirname(__file__)+"/support/dodf_pdfs/"
    targets = ["cmd", "extract", "-i", folder, "-a", "-c"]
    with patch.object(sys, 'argv', targets):
        run()
        for act in act_choices:
            assert os.path.isfile(folder+act+".csv")
            os.remove(folder+act+".csv")
    shutil.rmtree(folder + '/results')


def test_run_extract_input_folder_xml():
    folder = ""+os.path.dirname(__file__)+"/support/xml_extract"
    targets = ["cmd", "extract", "-i", folder, "-x"]
    with patch.object(sys, 'argv', targets):
        run()
        assert os.path.isfile(os.path.join(folder, '1_10.1.2020.xml'))
        os.remove(folder+'/1_10.1.2020.xml')

# def test_run_extract_input_single_xml():
#   file = ""+os.path.dirname(__file__)+"/support/xml_extract/DODF 001 02-01-2020 INTEGRA.pdf"
#   targets = ["cmd", "extract", "-s", file, "-x"]
#   with patch.object(sys, 'argv', targets):
#     run()
#     res_file = ""+os.path.dirname(__file__)+"/support/xml_extract/1_1.2.1.2020.xml"
#     assert os.path.isfile(res_file)
#     os.remove(res_file)
