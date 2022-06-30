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


def test_downloader_model_prop_abono(requests_mock):
    requests_mock.get('http://164.41.76.30/models/atos_pessoal/models/v1/abono.pkl')

    downloader = Downloader()
    downloader.pull(type_downloader="models", act_id="Abono", model_type="prop")


def test_downloader_model_seg_abono(requests_mock):
    requests_mock.get('http://164.41.76.30/models/atos_pessoal/seg_models/v1/abono.pkl')

    downloader = Downloader()
    downloader.pull(type_downloader="models", act_id="Abono", model_type="seg")


def test_downloader_model_prop_aposentadoria(requests_mock):
    requests_mock.get('http://164.41.76.30/models/atos_pessoal/models/v1/aposentadoria.pkl')

    downloader = Downloader()
    downloader.pull(type_downloader="models", act_id="Aposentadoria", model_type="prop")


def test_downloader_model_seg_aposentadoria(requests_mock):
    requests_mock.get('http://164.41.76.30/models/atos_pessoal/seg_models/v1/aposentadoria.pkl')

    downloader = Downloader()
    downloader.pull(type_downloader="models", act_id="Aposentadoria", model_type="seg")


def test_downloader_model_prop_cessoes(requests_mock):
    requests_mock.get('http://164.41.76.30/models/atos_pessoal/models/v1/cessao.pkl')

    downloader = Downloader()
    downloader.pull(type_downloader="models", act_id="Cessoes", model_type="prop")


def test_downloader_model_seg_cessoes(requests_mock):
    requests_mock.get('http://164.41.76.30/models/atos_pessoal/seg_models/v1/cessao.pkl')

    downloader = Downloader()
    downloader.pull(type_downloader="models", act_id="Cessoes", model_type="seg")


def test_downloader_model_prop_contrato(requests_mock):
    requests_mock.get('http://164.41.76.30/models/contratos/v1/gold_extratos_contrato-cnn_cnn_lstm.pkl')

    requests_mock.get('http://164.41.76.30/models/contratos/v1/tag2idx.pkl')

    requests_mock.get('http://164.41.76.30/models/contratos/v1/word2idx.pkl')

    requests_mock.get('http://164.41.76.30/models/contratos/v1/char2idx.pkl')

    downloader = Downloader()
    downloader.pull(type_downloader="models", act_id="Contrato", model_type="prop")


def test_downloader_model_seg_contrato(requests_mock):
    requests_mock.get('http://164.41.76.30/models/atos_pessoal/seg_models/v1/contrato.pkl')

    downloader = Downloader()
    downloader.pull(type_downloader="models", act_id="Contrato", model_type="seg")


def test_downloader_model_prop_exoneracao(requests_mock):
    requests_mock.get('http://164.41.76.30/models/atos_pessoal/models/v1/comissionados_exo.pkl')

    requests_mock.get('http://164.41.76.30/models/atos_pessoal/models/v1/efetivos_exo.pkl')

    downloader = Downloader()
    downloader.pull(type_downloader="models", act_id="Exoneracao", model_type="prop")


def test_downloader_model_seg_exoneracao(requests_mock):
    requests_mock.get('http://164.41.76.30/models/atos_pessoal/seg_models/v1/comissionados_exo.pkl')

    requests_mock.get('http://164.41.76.30/models/atos_pessoal/seg_models/v1/efetivos_exo.pkl')

    downloader = Downloader()
    downloader.pull(type_downloader="models", act_id="Exoneracao", model_type="seg")


def test_downloader_model_prop_nomeacao(requests_mock):
    requests_mock.get('http://164.41.76.30/models/atos_pessoal/models/v1/comissionados_nome.pkl')

    requests_mock.get('http://164.41.76.30/models/atos_pessoal/models/v1/efetivos_nome.pkl')

    downloader = Downloader()
    downloader.pull(type_downloader="models", act_id="Nomeacao", model_type="prop")


def test_downloader_model_seg_nomeacao(requests_mock):
    requests_mock.get('http://164.41.76.30/models/atos_pessoal/seg_models/v1/comissionados_nome.pkl')

    requests_mock.get('http://164.41.76.30/models/atos_pessoal/seg_models/v1/efetivos_nome.pkl')

    downloader = Downloader()
    downloader.pull(type_downloader="models", act_id="Nomeacao", model_type="seg")


def test_downloader_model_prop_reversoes(requests_mock):
    requests_mock.get('http://164.41.76.30/models/atos_pessoal/models/v1/reversao.pkl')

    downloader = Downloader()
    downloader.pull(type_downloader="models", act_id="Reversoes", model_type="prop")


def test_downloader_model_seg_reversoes(requests_mock):
    requests_mock.get('http://164.41.76.30/models/atos_pessoal/seg_models/v1/reversao.pkl')

    downloader = Downloader()
    downloader.pull(type_downloader="models", act_id="Reversoes", model_type="seg")


def test_downloader_model_prop_sem_efeito_aposentadoria(requests_mock):
    requests_mock.get('http://164.41.76.30/models/atos_pessoal/models/v1/sem_efeito_apo.pkl')

    downloader = Downloader()
    downloader.pull(type_downloader="models", act_id="SemEfeitoAposentadoria", model_type="prop")


def test_downloader_model_seg_sem_efeito_aposentadoria(requests_mock):
    requests_mock.get('http://164.41.76.30/models/atos_pessoal/seg_models/v1/sem_efeito_apo.pkl')

    downloader = Downloader()
    downloader.pull(type_downloader="models", act_id="SemEfeitoAposentadoria", model_type="seg")


def test_downloader_model_prop_substituicao(requests_mock):
    requests_mock.get('http://164.41.76.30/models/atos_pessoal/models/v1/substituicao.pkl')

    downloader = Downloader()
    downloader.pull(type_downloader="models", act_id="Substituicao", model_type="prop")


def test_downloader_model_prop_substituicao(requests_mock):
    requests_mock.get('http://164.41.76.30/models/atos_pessoal/seg_models/v1/substituicao.pkl')

    downloader = Downloader()
    downloader.pull(type_downloader="models", act_id="Substituicao", model_type="seg")


def test_downloader_all_models():
    downloader = Downloader()
    downloader.pull(type_downloader="models", act_id="all")


def test_downloader_all_embeddings():
    downloader = Downloader()
    downloader.pull(type_downloader="embeddings", embedding_id="all")