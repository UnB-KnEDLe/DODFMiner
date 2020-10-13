import os
import re
import pytest
import joblib
import sklearn_crfsuite
from unittest.mock import patch

from dodfminer.extract.pure.utils import title_filter

@pytest.fixture(scope='module')
def filter_class():
    return title_filter.BoldUpperCase

def test_dict_text(filter_class):
    # Can be a title
    d = {
        'text': "SECRETARIA DE PESSOAL DO DISTRITO FEDERAL",
    } 
    assert filter_class.dict_text(d) == True

def test_dict_text2(filter_class):
    # Can not be a title since has 4+ consecutive spaces
    d = {
        'text': "SECRETARIA    DE PESSOAL DO DISTRITO FEDERAL",
    } 
    assert filter_class.dict_text(d) == False

def test_dict_text3(filter_class):
    # Can not be a title since has lower case chars
    d = {
        'text': "SECRETARIA DE pessoal DO DISTRITO FEDERAL",
    } 
    assert filter_class.dict_text(d) == False

def test_dict_text4(filter_class):
    # Can not be a title since has 4- chars
    d = {
        'text': "BOM",
    } 
    assert filter_class.dict_text(d) == False

def test_dict_bold(filter_class):
    d = {
        'flags': 14
    }
    assert filter_class.dict_bold(d) == False

def test_dict_bold2(filter_class):
    d = {
        'flags': 16
    }
    assert filter_class.dict_bold(d) == True


def test_dict_bold3(filter_class):
    d = {
        'flags': 18
    }
    assert filter_class.dict_bold(d) == False

def test_dict_bold4(filter_class):
    d = {
        'flags': 20
    }
    assert filter_class.dict_bold(d) == True



