import pytest
from dodfminer.downloader.helper import req1, req2, req3, get_downloads, check_date, LISTAR_URL


def test_req1():
    assert req1(2017) == f'{LISTAR_URL}dir=2017'


def test_req2(requests_mock):
    # Cria um mock do retorno da requisicao
    requests_mock.get(f'{LISTAR_URL}dir=2017/01_Janeiro', json={
        "data": {
            "20170131100": "DODF 022 31-01-2017",
            "20170130103": "DODF 003 30-01-2017 EDICAO EXTRA",
        }
    })
    assert isinstance(
        req2(f'{LISTAR_URL}dir=2017', '01_Janeiro'), tuple)


def test_req2_2():
    with pytest.raises(ValueError):
        assert req2(f'{LISTAR_URL}dir=2017', 'Janeiro')


def test_req3(requests_mock):
    requests_mock.get(f'{LISTAR_URL}dir=2017/DODF%20023%2031-01-2006', json={
        "data": {
            "20170131100": "DODF 022 31-01-2017",
            "20170130103": "DODF 003 30-01-2017 EDICAO EXTRA",
        }
    })
    assert isinstance(req3(f'{LISTAR_URL}dir=2017',
                'DODF 023 31-01-2006'), tuple)


def test_get_downloads(requests_mock):
    # Primeira requisicao
    requests_mock.get(f'{LISTAR_URL}dir=2017/01_Janeiro', json={
        "data": {
            "20170131100": "DODF 022 31-01-2017",
            "20170130103": "DODF 003 30-01-2017 EDICAO EXTRA",
        }
    })
    # Segunda requisicao
    requests_mock.get(f'{LISTAR_URL}dir=2017/01_Janeiro/DODF%20022%2031-01-2017', json={
        "data": {
            "UNIT": "Test",
        }
    })
    # Terceira requisicao
    requests_mock.get(f'{LISTAR_URL}dir=2017/01_Janeiro/DODF%20003%2030-01-2017%20EDICAO EXTRA', json={
        "data": {
            "UNIT": "Test2",
        }
    })

    assert isinstance(get_downloads('2017', '01_Janeiro'), dict)


def test_get_downloads_2():
    with pytest.raises(ValueError):
        assert get_downloads('2017', 'Janeiro')


def test_check_date(requests_mock):
    requests_mock.get(f'{LISTAR_URL}dir=2017/01_Janeiro', json={
        "data": {
            "Unit": "Test"
        }
    })
    # Deve retornar true
    assert check_date('2017', '01_Janeiro')

    requests_mock.get(f'{LISTAR_URL}dir=2017/01_Janeiro', json={
        "data": {}
    })
    # Deve retornar false
    assert not check_date('2017', '01_Janeiro')

    requests_mock.get(
        f'{LISTAR_URL}dir=2017/01_Janeiro', json={})
    # Deve retornar false
    assert not check_date('2017', '01_Janeiro')


def test_check_date_2():
    with pytest.raises(ValueError):
        assert check_date('2017', 'Janeiro')
