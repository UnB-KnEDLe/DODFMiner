# pylint: disable=protected-access

import os
from unittest.mock import patch
import joblib
import pytest
from dodfminer.extract.polished.backend.seg import ActSeg

# act_seg with regex segmentation

@pytest.fixture(name='act_seg_regex')
@patch.object(ActSeg, '_backend', create = True)
def fixture_act_seg_regex(*_):
    act = ActSeg()
    act._name = 'test'
    act._backend = 'regex'

    act._flags = 0
    act._rules = {
        "numeros": r"([0-9]+)",
        "capitalizado": r"([A-Z][a-z]+)",
        "nao_encontra": "khalil"
    }
    act._inst_rule = r"(MENSAGEM:)([^.]*)"
    act._acts_str = []

    act.__init__()
    return act

def test_act_seg_regex(act_seg_regex):
    assert act_seg_regex._backend == 'regex'
    assert act_seg_regex._seg_function == act_seg_regex._regex_instances

# act_seg with ner segmentation

@pytest.fixture(name='act_seg_ner')
@patch.object(ActSeg, '_backend', create = True)
@patch.object(ActSeg, '_load_seg_model',
              return_value=joblib.load(""+os.path.dirname(__file__)+"/support/test_seg_model.pkl"))
def fixture_act_seg_ner(*_):
    act = ActSeg()
    act._name = 'test'
    act._backend = 'ner'
    act.__init__()
    return act

def test_act_seg_ner(act_seg_ner):
    assert act_seg_ner._backend == 'ner'
    assert act_seg_ner._seg_function == act_seg_ner._crf_instances

# act_seg with ner background but no model, reverting to regex segmentation

@pytest.fixture(name='act_seg_reverting_to_regex')
@patch.object(ActSeg, '_backend', create = True)
def fixture_act_seg_reverting_to_regex(*_):
    act = ActSeg()
    act._name = 'test'
    act._backend = 'ner'
    act.__init__()
    return act

def test_act_seg_reverting_to_regex(act_seg_reverting_to_regex):
    assert act_seg_reverting_to_regex._backend == 'ner'
    assert act_seg_reverting_to_regex._seg_function == act_seg_reverting_to_regex._regex_instances

#

def test_act_seg_regex_instances(act_seg_regex):
    act_seg_regex._text =  "fghngfnfgnfgnfgnrr MENSAGEM: O Renato testa esse codigo 1232 vezes por dia. qeqcnoecqucqpwxqrthrweqqeprto MENSAGEM: " + \
        "O Joao testa esse codigo 2 vezes por dia. wsfhsn wenrwermrkne MENSAGEM: O Lucas testa esse codigo 0 vezes por dia. efwefwefwfwefwetrynyujuju"
    act_seg_regex.acts_str = []
    act = act_seg_regex._seg_function()

    assert act == [' O Renato testa esse codigo 1232 vezes por dia',
                   ' O Joao testa esse codigo 2 vezes por dia', ' O Lucas testa esse codigo 0 vezes por dia']

def test_act_seg_crf_instances(act_seg_ner):
    act_seg_ner._text = "CONCEDER, aposentadoria voluntária integral, ao servidor ELIAS SANTOS MONTEIRO, matrícula nº 24.679-4, no cargo de " + \
        "Analista em Políticas Públicas e Gestão Governamental, Classe Especial, Padrão V, do Quadro de Pessoal do Distrito Federal, nos termos " + \
        "do artigo 3º, incisos I, II e III, e Parágrafo único da Emenda Constitucional nº 47 de 05/07/2005, combinado com o artigo 44 da Lei " + \
        "Complementar nº 769, de 30/06/2008, e com a vantagem pessoal prevista no artigo 5º da Lei nº 4.584, de 08/07/2011. Lotação: " + \
        "Administração Regional de Brazlândia. Processo SEI nº 00133-00002749/2020-19. CONCEDER, aposentadoria voluntária integral, à servidora " + \
        "MIRIAM RODRIGUES DA SILVA, matrícula nº 31.325-4, no cargo de Analista em Políticas Públicas e Gestão Governamental, Classe Especial, " + \
        "Padrão V, do Quadro de Pessoal do Distrito Federal, nos termos do artigo 3º, incisos I, II e III, e Parágrafo único da Emenda " + \
        "Constitucional nº 47 de 05/07/2005, combinado com o artigo 44 da Lei Complementar nº 769, de 30/06/2008, e com a vantagem pessoal " + \
        "prevista no artigo 5º da Lei nº 4.584, de 08/07/2011. Lotação: Administração Regional de Brazlândia. Processo SEI nº " + \
        "00133-00002735/2020-97"
    act_seg_ner._acts_str = []
    act = act_seg_ner._seg_function()

    assert len(act) == 2

def test_act_seg_preprocess(act_seg_ner):
    text = "CONCEDER, aposentadoria voluntária integral, ao servidor ELIAS SANTOS MONTEIRO, matrícula nº 24.679-4, no cargo de " + \
        "Analista em Políticas Públicas e Gestão Governamental, Classe Especial, Padrão V, do Quadro de Pessoal do Distrito Federal, nos termos " + \
        "do artigo 3º, incisos I, II e III, e Parágrafo único da Emenda Constitucional nº 47 de 05/07/2005, combinado com o artigo 44 da Lei " + \
        "Complementar nº 769, de 30/06/2008, e com a vantagem pessoal prevista no artigo 5º da Lei nº 4.584, de 08/07/2011. Lotação: " + \
        "Administração Regional de Brazlândia. Processo SEI nº 00133-00002749/2020-19."
    preprocessed_text = ['CONCEDER', ',', 'aposentadoria', 'voluntária', 'integral', ',', 'ao', 'servidor', 'ELIAS', 'SANTOS', 'MONTEIRO', ',',
        'matrícula', 'nº', '24', '.', '679', '-', '4', ',', 'no', 'cargo', 'de', 'Analista', 'em', 'Políticas', 'Públicas', 'e', 'Gestão',
        'Governamental', ',', 'Classe', 'Especial', ',', 'Padrão', 'V', ',', 'do', 'Quadro', 'de', 'Pessoal', 'do', 'Distrito', 'Federal', ',',
        'nos', 'termos', 'do', 'artigo', '3º', ',', 'incisos', 'I', ',', 'II', 'e', 'III', ',', 'e', 'Parágrafo', 'único', 'da', 'Emenda',
        'Constitucional', 'nº', '47', 'de', '05', '/', '07', '/', '2005', ',', 'combinado', 'com', 'o', 'artigo', '44', 'da', 'Lei', 'Complementar',
        'nº', '769', ',', 'de', '30', '/', '06', '/', '2008', ',', 'e', 'com', 'a', 'vantagem', 'pessoal', 'prevista', 'no', 'artigo', '5º', 'da',
        'Lei', 'nº', '4', '.', '584', ',', 'de', '08', '/', '07', '/', '2011', '.', 'Lotação', ':', 'Administração', 'Regional', 'de', 'Brazlândia',
        '.', 'Processo', 'SEI', 'nº', '00133', '-', '00002749', '/', '2020', '-', '19', '.']
    assert act_seg_ner._preprocess(text) == preprocessed_text

def test_act_seg_number_of_digits(act_seg_ner):
    text = "123abc456"
    assert act_seg_ner._number_of_digits(text) == 6


def test_act_seg_get_base_feat(act_seg_ner):
    word = "NER"
    assert act_seg_ner._get_base_feat(word) == {
        'word': 'ner',
        'is_title': False,
        'is_upper': True,
        'num_digits': '0',
    }


def test_act_seg_get_features(act_seg_ner):
    text = "CONCEDER , servidor ELIAS 24.679-4".split()
    features = [
        {
            'bias': 1.0, 'word': 'conceder', 'is_title': False, 'is_upper': True, 'num_digits': '0', 'BOS': True, '+1:word': ',', '+1:title': False,
            '+1:upper': False, '+1:num_digits': '0', '+2:word': 'servidor', '+2:title': False, '+2:upper': False, '+2:num_digits': '0',
            '+3:word': 'elias', '+3:title': False, '+3:upper': True, '+3:num_digits': '0', '+4:word': '24.679-4', '+4:title': False,
            '+4:upper': False, '+4:num_digits': '6'
        },
        {
            'bias': 1.0, 'word': ',', 'is_title': False, 'is_upper': False, 'num_digits': '0', '-1:word': 'conceder', '-1:title': False,
            '-1:upper': True, '-1:num_digits': '0', '+1:word': 'servidor', '+1:title': False, '+1:upper': False, '+1:num_digits': '0',
            '+2:word': 'elias', '+2:title': False, '+2:upper': True, '+2:num_digits': '0', '+3:word': '24.679-4', '+3:title': False,
            '+3:upper': False, '+3:num_digits': '6'
        },
        {
            'bias': 1.0, 'word': 'servidor', 'is_title': False, 'is_upper': False, 'num_digits': '0', '-1:word': ',', '-1:title': False,
            '-1:upper': False, '-1:num_digits': '0', '-2:word': 'conceder', '-2:title': False, '-2:upper': True, '-2:num_digits': '0',
            '+1:word': 'elias', '+1:title': False, '+1:upper': True, '+1:num_digits': '0', '+2:word': '24.679-4', '+2:title': False,
            '+2:upper': False, '+2:num_digits': '6'
        },
        {
            'bias': 1.0, 'word': 'elias', 'is_title': False, 'is_upper': True, 'num_digits': '0', '-1:word': 'servidor', '-1:title': False,
            '-1:upper': False, '-1:num_digits': '0', '-2:word': ',', '-2:title': False, '-2:upper': False, '-2:num_digits': '0',
            '-3:word': 'conceder', '-3:title': False, '-3:upper': True, '-3:num_digits': '0', '+1:word': '24.679-4', '+1:title': False,
            '+1:upper': False, '+1:num_digits': '6'
        },
        {
            'bias': 1.0, 'word': '24.679-4', 'is_title': False, 'is_upper': False, 'num_digits': '6', '-1:word': 'elias', '-1:title': False,
            '-1:upper': True, '-1:num_digits': '0', '-2:word': 'servidor', '-2:title': False, '-2:upper': False, '-2:num_digits': '0',
            '-3:word': ',', '-3:title': False, '-3:upper': False, '-3:num_digits': '0', '-4:word': 'conceder', '-4:title': False,
            '-4:upper': True, '-4:num_digits': '0', 'EOS': True
        }]

    assert act_seg_ner._get_features(text) == features


def test_act_seg_extract_acts(act_seg_ner):
    text = "AAAA  BBBB  CCCC  DDDD EEEE FFFF  XXXX  YYYY  ZZZZ".split()
    pred = "B-Ato I-Ato E-ato O    O    B-Ato I-Ato E-Ato O".split()
    alvo =["AAAA BBBB CCCC",            "FFFF XXXX YYYY"]

    assert act_seg_ner._extract_acts(text, pred) == alvo
