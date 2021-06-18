import pytest
from dodfminer.downloader.helper import req1, req2, req3, get_downloads, check_date   


def test_req1():
    assert req1(2017) == 'https://dodf.df.gov.br/listar?dir=2017' 

def test_req2():
    assert  type(req2('https://dodf.df.gov.br/listar?dir=2017', '01_Janeiro')) == tuple

def test_req2_2():
    with pytest.raises(ValueError):
        assert (req2('https://dodf.df.gov.br/listar?dir=2017', 'Janeiro'))

def test_req3():
    assert  type(req3('https://dodf.df.gov.br/listar?dir=2017', 'DODF 023 31-01-2006')) == tuple

def test_get_downloads():
    assert type(get_downloads('2017', '01_Janeiro')) == dict

def test_get_downloads_2():
    with pytest.raises(ValueError):
        assert (get_downloads('2017', 'Janeiro'))

def test_check_date():
    assert type(check_date('2017', '01_Janeiro')) == bool

def test_check_date_2():
    with pytest.raises(ValueError):
        assert (check_date('2017', 'Janeiro'))