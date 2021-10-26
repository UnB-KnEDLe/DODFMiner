import shutil
import pytest
import requests
from dodfminer.downloader.core import Downloader
from dodfminer.downloader.helper import LISTAR_URL


def test_download_date_fail():
    with pytest.raises(Exception):
        downloader = Downloader()
        downloader.pull(start_date="05\\2021", end_date="1006\\2021")


def test_download_date_fail_2(requests_mock):
    requests_mock.get(
        f'{LISTAR_URL}dir=2021/05_Maio', json={})
    requests_mock.get(
        f'{LISTAR_URL}dir=2021/06_Junho', json={})
    downloader = Downloader()
    downloader.pull(start_date="05/2021", end_date="06/2021")


def test_downloader_fail(requests_mock):

    requests_mock.get(f'{LISTAR_URL}dir=2021/05_Maio', json={
        "data": {
            "20170131100": "DODF 022 31-01-2017",
        }
    })
    requests_mock.get(f'{LISTAR_URL}dir=2021/05_Maio/DODF%20022%2031-01-2017', json={
        "data": {
            "UNIT": "Test",
        }
    })
    requests_mock.get(f'{LISTAR_URL}dir=2021/05_Maio/DODF%20003%2030-01-2017%20EDICAO EXTRA', json={
        "data": {
            "UNIT": "Test2",
        }
    })

    requests_mock.register_uri('GET',
                               'https://dodf.df.gov.br/index/visualizar-arquivo/?pasta=2021%7C05_Maio%7CDODF%20022%2031-01-2017%7C&arquivo=UNIT',
                               exc=requests.exceptions.HTTPError)
    downloader = Downloader()
    downloader.pull(start_date="05-2021", end_date="05-2021")


def test_downloader(requests_mock):
    # Remove conteudo inicial
    shutil.rmtree('dodfs/2021', ignore_errors=True)

    requests_mock.get(f'{LISTAR_URL}dir=2021/05_Maio', json={
        "data": {
            "20170131100": "DODF 022 31-01-2017",
            "20170130103": "DODF 003 30-01-2017 EDICAO EXTRA",
        }
    })
    requests_mock.get(f'{LISTAR_URL}dir=2021/05_Maio/DODF%20022%2031-01-2017', json={
        "data": {
            "UNIT": "Test",
        }
    })
    requests_mock.get(f'{LISTAR_URL}dir=2021/05_Maio/DODF%20003%2030-01-2017%20EDICAO EXTRA', json={
        "data": {
            "UNIT": "Test2",
        }
    })

    requests_mock.get(
        'https://dodf.df.gov.br/index/visualizar-arquivo/?pasta=2021%7C05_Maio%7CDODF%20022%2031-01-2017%7C&arquivo=UNIT', json={})
    requests_mock.get(
        'https://dodf.df.gov.br/index/visualizar-arquivo/?pasta=2021%7C05_Maio%7CDODF%20003%2030-01-2017%20EDICAO%20EXTRA%7C&arquivo=UNIT', json={})

    requests_mock.get(f'{LISTAR_URL}dir=2021/06_Junho', json={
        "data": {
            "20170131100": "DODF 022 31-01-2017",
            "20170130103": "DODF 003 30-01-2017 EDICAO EXTRA",
        }
    })
    requests_mock.get(f'{LISTAR_URL}dir=2021/06_Junho/DODF%20022%2031-01-2017', json={
        "data": {
            "UNIT": "Test",
        }
    })
    requests_mock.get(f'{LISTAR_URL}dir=2021/06_Junho/DODF%20003%2030-01-2017%20EDICAO EXTRA', json={
        "data": {
            "UNIT": "Test2",
        }
    })

    requests_mock.get(
        'https://dodf.df.gov.br/index/visualizar-arquivo/?pasta=2021%7C06_Junho%7CDODF%20022%2031-01-2017%7C&arquivo=UNIT', json={})
    requests_mock.get(
        'https://dodf.df.gov.br/index/visualizar-arquivo/?pasta=2021%7C06_Junho%7CDODF%20003%2030-01-2017%20EDICAO%20EXTRA%7C&arquivo=UNIT', json={})

    downloader = Downloader()
    downloader.pull(start_date="05/2021", end_date="06/2021")


def test_downloader_2(requests_mock):
    requests_mock.get(f'{LISTAR_URL}dir=2021/05_Maio', json={
        "data": {
            "20170131100": "DODF 022 31-01-2017",
        }
    })
    requests_mock.get(f'{LISTAR_URL}dir=2021/05_Maio/DODF%20022%2031-01-2017', json={
        "data": {
            "UNIT": "Test",
        }
    })
    requests_mock.get(f'{LISTAR_URL}dir=2021/05_Maio/DODF%20003%2030-01-2017%20EDICAO EXTRA', json={
        "data": {
            "UNIT": "Test2",
        }
    })

    requests_mock.get(
        'https://dodf.df.gov.br/index/visualizar-arquivo/?pasta=2021%7C05_Maio%7CDODF%20022%2031-01-2017%7C&arquivo=UNIT', json={})
    downloader = Downloader()
    downloader.pull(start_date="05-2021", end_date="05-2021")
