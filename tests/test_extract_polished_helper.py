import os
import pytest

import pandas as pd
from pandas.core.frame import DataFrame

from dodfminer.extract.pure.core import ContentExtractor
from dodfminer.extract.polished.acts.nomeacao import NomeacaoComissionados
from dodfminer.extract.polished.helper import xml_multiple, get_files_path, print_dataframe, build_act_txt, extract_single, extract_multiple, extract_multiple_acts

from decorators import clean_extra_files

FOLDER_PATH = f"{os.path.dirname(__file__)}/support/polished"

###################### FIXTURES ######################

@pytest.fixture
def folder_path():
    return FOLDER_PATH

@pytest.fixture
def file_path(folder_path):
    def _file_path(extension="pdf"):
        return f"{folder_path}/DODF 001 01-01-2019 EDICAO ESPECIAL.{extension}"
    return _file_path


###################### TESTS ######################
@clean_extra_files(FOLDER_PATH)
def test_helper_xml_multiple(folder_path):
    try:
        xml_multiple(folder_path, "regex")
        xml_files_list = list(filter(lambda x : ".xml" in x, os.listdir(folder_path)))

        assert "1_1.1.2019.xml" in xml_files_list
    except:
        assert False

@clean_extra_files(FOLDER_PATH)
def test_helper_extract_multiple(folder_path):
    ContentExtractor.extract_to_txt(folder_path)
    files = get_files_path(f"{folder_path}/results/txt", 'txt')
    df = extract_multiple(files, "nomeacao", "regex", txt_path="./results")

    assert len(df) > 0

@clean_extra_files(FOLDER_PATH)
def test_helper_extract_single(file_path):
    ContentExtractor.extract_text(file_path(extension="pdf"), single=True)
    df, texts, obj = extract_single(file_path(extension="txt"), "nomeacao", "regex")

    assert type(df) is DataFrame
    assert type (texts) is list
    assert type(obj) is NomeacaoComissionados

    assert len(df) > 0
    assert len(texts) > 0

@clean_extra_files(FOLDER_PATH)
def test_helper_extract_multiple_acts(folder_path, file_path):
    extract_multiple_acts(folder_path, ["nomeacao"], "regex")
    multiple_files_df = pd.read_csv(f"{folder_path}/nomeacao.csv")
    extract_multiple_acts(file_path(extension="pdf"), ["nomeacao"], "regex")
    single_file_df = pd.read_csv(f"{folder_path}/nomeacao.csv")

    assert len(multiple_files_df) > 0
    assert len(single_file_df) > 0
    assert len(multiple_files_df) > len(single_file_df)

@clean_extra_files(FOLDER_PATH)
def test_helper_build_act_txt():
    dir = ""+os.path.dirname(__file__)+"/support/"
    build_act_txt(["aposentadoria"], "crioutxt", save_path=dir)
    
    assert "crioutxt.txt" in os.listdir(dir)

    os.remove(os.path.join(dir, "crioutxt.txt"))

# def test_helper_print_dataframe():
#     df = print_dataframe(pd.DataFrame())
#     assert isinstance(df, pd.io.formats.style.Styler)

def test_helper_get_files_path(folder_path):
    files = get_files_path(folder_path, "txt")
    assert len(files) == 1
    files = get_files_path(folder_path, "pdf")
    assert len(files) == 2

