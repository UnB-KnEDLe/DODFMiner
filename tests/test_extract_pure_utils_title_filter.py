import pytest

from dodfminer.extract.pure.utils import title_filter


@pytest.fixture(name='filter_class', scope='module')
def fixture_filter_class():
    return title_filter.BoldUpperCase


def test_dict_text(filter_class):
    # Can be a title
    assert filter_class.dict_text({
        'text': "SECRETARIA DE PESSOAL DO DISTRITO FEDERAL",
    }) is True


def test_dict_text2(filter_class):
    # Can not be a title since has 4+ consecutive spaces
    assert filter_class.dict_text({
        'text': "SECRETARIA    DE PESSOAL DO DISTRITO FEDERAL",
    }) is False


def test_dict_text3(filter_class):
    # Can not be a title since has lower case chars
    assert filter_class.dict_text({
        'text': "SECRETARIA DE pessoal DO DISTRITO FEDERAL",
    }) is False


def test_dict_text4(filter_class):
    # Can not be a title since has 4- chars
    assert filter_class.dict_text({
        'text': "BOM",
    }) is False


def test_dict_bold(filter_class):
    assert filter_class.dict_bold({
        'flags': 14
    }) is False


def test_dict_bold2(filter_class):
    assert filter_class.dict_bold({
        'flags': 16
    }) is True


def test_dict_bold3(filter_class):
    assert filter_class.dict_bold({
        'flags': 18
    }) is False


def test_dict_bold4(filter_class):
    assert filter_class.dict_bold({
        'flags': 20
    }) is True
