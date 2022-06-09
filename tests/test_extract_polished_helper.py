import os
import pytest

import pandas as pd
from pandas.core.frame import DataFrame

from tests.helpers.decorators import clean_extra_files

from dodfminer.extract.pure.core import ContentExtractor
from dodfminer.extract.polished.helper import xml_multiple, get_files_path, build_act_txt, extract_single, extract_multiple, \
    extract_multiple_acts, extract_multiple_acts_with_committee, committee_classification, extract_multiple_acts_parallel


FOLDER_PATH = f"{os.path.dirname(__file__)}/support/polished"

###################### FIXTURES ######################


@pytest.fixture(name="folder_path")
def fixture_folder_path():
    return FOLDER_PATH


@pytest.fixture(name="file_path")
def fixture_file_path(folder_path):
    def _file_path(extension="pdf"):
        return f"{folder_path}/DODF 001 01-01-2019 EDICAO ESPECIAL.{extension}"
    return _file_path


###################### TESTS ######################
@clean_extra_files(FOLDER_PATH)
def test_helper_xml_multiple(folder_path):
    try:
        xml_multiple(folder_path, "regex")
        xml_files_list = list(
            filter(lambda x: ".xml" in x, os.listdir(folder_path)))

        assert "1_1.1.2019.xml" in xml_files_list
    except AssertionError:
        assert False


@clean_extra_files(FOLDER_PATH)
def test_helper_extract_multiple(folder_path):
    ContentExtractor.extract_to_txt(folder_path)
    files = get_files_path(f"{folder_path}/results/txt", 'txt')
    data_frame = extract_multiple(
        files, "nomeacao", "regex", txt_path="./results")

    assert len(data_frame) > 0


@clean_extra_files(FOLDER_PATH)
def test_helper_extract_single(file_path):
    ContentExtractor.extract_text(file_path(extension="pdf"), single=True)
    data_frame, texts = extract_single(
        file_path(extension="txt"), "nomeacao", "regex")

    assert isinstance(data_frame, DataFrame)
    assert isinstance(texts, list)

    assert len(data_frame) > 0
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
def test_helper_extract_multiple_acts_parallel(folder_path, file_path):
    extract_multiple_acts_parallel(folder_path, ["nomeacao"], "regex")
    multiple_files_df = pd.read_csv(f"{folder_path}/nomeacao.csv")
    extract_multiple_acts_parallel(
        file_path(extension="pdf"), ["nomeacao"], "regex")
    single_file_df = pd.read_csv(f"{folder_path}/nomeacao.csv")

    assert len(multiple_files_df) > 0
    assert len(single_file_df) > 0
    assert len(multiple_files_df) > len(single_file_df)


@clean_extra_files(FOLDER_PATH)
def test_helper_extract_multiple_acts_with_committee(folder_path, file_path):
    extract_multiple_acts_with_committee(folder_path, ["nomeacao"], "regex")
    multiple_files_df = pd.read_csv(f"{folder_path}/nomeacao.csv")

    extract_multiple_acts_with_committee(
        file_path(extension="pdf"), ["nomeacao"], "regex")
    single_file_df = pd.read_csv(f"{folder_path}/nomeacao.csv")

    assert len(multiple_files_df) > 0
    assert len(single_file_df) > 0
    assert len(multiple_files_df) > len(single_file_df)


@clean_extra_files(FOLDER_PATH)
def test_helper_committee_classification(folder_path, file_path):
    dataframe = pd.read_csv(f"{folder_path}/nomeacao_extraida.csv")
    dataframe = dataframe.filter(['Tipo do Ato', 'text'], axis=1)
    dataframe.columns = ['type', 'text']

    committee_classification(dataframe, file_path(
        extension="pdf"), ["nomeacao"], "regex")
    output_df = pd.read_csv(f"{folder_path}/nomeacao.csv")

    assert len(output_df) == len(dataframe)


@clean_extra_files(FOLDER_PATH)
def test_helper_build_act_txt():
    directory = ""+os.path.dirname(__file__)+"/support/"
    build_act_txt(["aposentadoria"], "crioutxt", save_path=directory)
    assert "crioutxt.txt" in os.listdir(directory)
    os.remove(os.path.join(directory, "crioutxt.txt"))

# def test_helper_print_dataframe():
#     df = print_dataframe(pd.DataFrame())
#     assert isinstance(df, pd.io.formats.style.Styler)


def test_helper_get_files_path(folder_path):
    files = get_files_path(folder_path, "txt")
    assert len(files) > 0
    files = get_files_path(folder_path, "pdf")
    assert len(files) > 0
