import os
import pandas as pd

from dodfminer.extract.polished.helper import xml_multiple, get_files_path, print_dataframe

def test_helper_xml_multiple():
    dir = ""+os.path.dirname(__file__)+"/support/"
    xml_multiple(dir, "regex")
    assert "12019.xml" in os.listdir(dir)
    os.remove(os.path.join(dir, "12019.xml"))

# def test_helper_extract_multiple_acts():
#     extract_multiple_acts(path, types, backend)

# def test_helper_extract_multiple():
#     extract_multiple(files, type, backend, txt_out=False, txt_path="./results")

# def test_helper_extract_single():
#     extract_single(file, type, backend)

# def test_helper_build_act_txt():
#     build_act_txt(acts, name, save_path="./results/")

def test_helper_print_dataframe():
    df = print_dataframe(pd.DataFrame())
    assert isinstance(df, pd.io.formats.style.Styler)

def test_helper_get_files_path():
    dir = ""+os.path.dirname(__file__)+"/support/"
    files = get_files_path(dir, "txt")
    assert files == [""+os.path.dirname(__file__)+'/support/valid.txt', ""+os.path.dirname(__file__)+'/support/support_supporter/valid.txt']
    files = get_files_path(dir, "pdf")
    assert files == [""+os.path.dirname(__file__)+'/support/DODF 001 01-01-2019 EDICAO ESPECIAL.pdf', ""+os.path.dirname(__file__)+'/support/support_supporter/DODF 001 01-01-2019 EDICAO ESPECIAL.pdf']

