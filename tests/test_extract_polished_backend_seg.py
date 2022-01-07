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

def test_act_seg_preprocess(act_seg_ner):
    sentence = "teste com\npalavras."
    assert act_seg_ner._preprocess(sentence) == 'teste com palavras.'

def test_act_seg_limits(act_seg_ner):
    sentence = "teste com palavras.123"
    assert act_seg_ner._limits(sentence) == [0, 6, 10, 18, 19]

def test_act_seg_regex_instances(act_seg_regex):
    act_seg_regex._text =  "fghngfnfgnfgnfgnrr MENSAGEM: O Renato testa esse codigo 1232 vezes por dia. qeqcnoecqucqpwxqrthrweqqeprto MENSAGEM: " + \
        "O Joao testa esse codigo 2 vezes por dia. wsfhsn wenrwermrkne MENSAGEM: O Lucas testa esse codigo 0 vezes por dia. efwefwefwfwefwetrynyujuju"
    act_seg_regex.acts_str = []
    act = act_seg_regex._seg_function()

    assert act == [' O Renato testa esse codigo 1232 vezes por dia',
                   ' O Joao testa esse codigo 2 vezes por dia', ' O Lucas testa esse codigo 0 vezes por dia']

def test_act_seg_crf_instances(act_seg_ner):
    act_seg_ner._text = ": CONCEDER, aposentadoria voluntaria integral, ao servidor ELIAS SANTOS MONTEIRO, matrícula nº 24.679-4, no cargo de " + \
        "Analista em Políticas Públicas e Gestão Governamental, Classe Especial, Padrão V, do Quadro de Pessoal do Distrito Federal, nos termos " + \
        "do artigo 3º, incisos I, II e III, e Parágrafo único da Emenda Constitucional nº 47 de 05/07/2005, combinado com o artigo 44 da Lei " + \
        "Complementar nº 769, de 30/06/2008, e com a vantagem pessoal prevista no artigo 5º da Lei nº 4.584, de 08/07/2011. Lotação: " + \
        "Administração Regional de Brazlândia. Processo SEI nº 00133-00002749/2020-19. CONCEDER, aposentadoria voluntaria integral, a servidora " + \
        "MIRIAM RODRIGUES DA SILVA, matricula nº 31.325-4, no cargo de Analista em Politicas Públicas e Gestao Governamental, Classe Especial, " + \
        "Padrão V, do Quadro de Pessoal do Distrito Federal, nos termos do artigo 3º, incisos I, II e III, e Parágrafo único da Emenda " + \
        "Constitucional nº 47 de 05/07/2005, combinado com o artigo 44 da Lei Complementar nº 769, de 30/06/2008, e com a vantagem pessoal " + \
        "prevista no artigo 5º da Lei nº 4.584, de 08/07/2011. Lotação: Administração Regional de Brazlândia. Processo SEI nº " + \
        "00133-00002735/2020-97."
    act_seg_ner._acts_str = []
    act = act_seg_ner._seg_function()

    assert len(act) == 2

def test_act_seg_split_sentences(act_seg_ner):
    text = "CONCEDER, aposentadoria voluntária integral, ao servidor ELIAS SANTOS MONTEIRO, matrícula nº 24.679-4, no cargo de " + \
        "Analista em Políticas Públicas e Gestão Governamental, nos termos..."
    preprocessed = ['CONCEDER', ',', 'aposentadoria', 'volunt', 'á', 'ria', 'integral', ',', 'ao', 'servidor', 'ELIAS', 'SANTOS', 'MONTEIRO', ',',
        'matr', 'í', 'cula', 'n', 'º', '24', '.', '679', '-', '4', ',', 'no', 'cargo', 'de', 'Analista', 'em', 'Pol', 'í', 'ticas', 'P', 'ú',
        'blicas', 'e', 'Gest', 'ã', 'o', 'Governamental', ',', 'nos', 'termos', '.', '.', '.']
    assert act_seg_ner._split_sentence(text) == preprocessed

def test_act_seg_get_base_feat(act_seg_ner):
    word = "NER"
    assert act_seg_ner._get_base_feat(word) == {
        'word': 'ner',
        'is_title': False,
        'is_upper': True,
        'num_digits': '0',
    }

def test_act_seg_add_base_feat(act_seg_ner):
    features = {'': 0}
    sentence = ["Teste001", "."]
    index = 1
    prefix = '+1:'

    feat_target = {'': 0, '+1:word': '.', '+1:is_title': False, '+1:is_upper': False, '+1:num_digits': '0'}

    act_seg_ner._add_base_feat(features, sentence, index, prefix)

    assert features == feat_target

def test_act_seg_get_features(act_seg_ner):
    sentence = ["Art", ".", "5", ",", "ATOS"]
    features_1 = [
        {
            'bias': 1.0,
            'text_position': 0.0,
            'word': 'art',
            'is_title': True,
            'is_upper': False,
            'num_digits': '0',
            '+1:word': '.',
            '+1:is_title': False,
            '+1:is_upper': False,
            '+1:num_digits': '0',
            '+2:word': '5',
            '+2:is_title': False,
            '+2:is_upper': False,
            '+2:num_digits': '1',
            '+3:word': ',',
            '+3:is_title': False,
            '+3:is_upper': False,
            '+3:num_digits': '0',
            '+4:word': 'atos',
            '+4:is_title': False,
            '+4:is_upper': True,
            '+4:num_digits': '0'
        },
        {
            'bias': 1.0,
            'text_position': 0.2,
            '-1:word': 'art',
            '-1:is_title': True,
            '-1:is_upper': False,
            '-1:num_digits': '0',
            'word': '.',
            'is_title': False,
            'is_upper': False,
            'num_digits': '0',
            '+1:word': '5',
            '+1:is_title': False,
            '+1:is_upper': False,
            '+1:num_digits': '1',
            '+2:word': ',',
            '+2:is_title': False,
            '+2:is_upper': False,
            '+2:num_digits': '0',
            '+3:word': 'atos',
            '+3:is_title': False,
            '+3:is_upper': True,
            '+3:num_digits': '0'
        },
        {
            'bias': 1.0,
            'text_position': 0.4,
            '-2:word': 'art',
            '-2:is_title': True,
            '-2:is_upper': False,
            '-2:num_digits': '0',
            '-1:word': '.',
            '-1:is_title': False,
            '-1:is_upper': False,
            '-1:num_digits': '0',
            'word': '5',
            'is_title': False,
            'is_upper': False,
            'num_digits': '1',
            '+1:word': ',',
            '+1:is_title': False,
            '+1:is_upper': False,
            '+1:num_digits': '0',
            '+2:word': 'atos',
            '+2:is_title': False,
            '+2:is_upper': True,
            '+2:num_digits': '0'
        },
        {
            'bias': 1.0,
            'text_position': 0.6,
            '-3:word': 'art',
            '-3:is_title': True,
            '-3:is_upper': False,
            '-3:num_digits': '0',
            '-2:word': '.',
            '-2:is_title': False,
            '-2:is_upper': False,
            '-2:num_digits': '0',
            '-1:word': '5',
            '-1:is_title': False,
            '-1:is_upper': False,
            '-1:num_digits': '1',
            'word': ',',
            'is_title': False,
            'is_upper': False,
            'num_digits': '0',
            '+1:word': 'atos',
            '+1:is_title': False,
            '+1:is_upper': True,
            '+1:num_digits': '0'
        },
        {
            'bias': 1.0,
            'text_position': 0.8,
            '-4:word': 'art',
            '-4:is_title': True,
            '-4:is_upper': False,
            '-4:num_digits': '0',
            '-3:word': '.',
            '-3:is_title': False,
            '-3:is_upper': False,
            '-3:num_digits': '0',
            '-2:word': '5',
            '-2:is_title': False,
            '-2:is_upper': False,
            '-2:num_digits': '1',
            '-1:word': ',',
            '-1:is_title': False,
            '-1:is_upper': False,
            '-1:num_digits': '0',
            'word': 'atos',
            'is_title': False,
            'is_upper': True,
            'num_digits': '0'
        }
    ]
    assert features_1 == act_seg_ner._get_features(sentence)


def test_act_seg_extract_acts(act_seg_ner):
    text = "OOOO AAAA BBBB CCCC DDDD EEEE FFFF XXXX YYYY ZZZZ"
    pred = "O B-Ato I-Ato E-ato O O B-Ato I-Ato E-Ato O".split()
    alvo =["AAAA BBBB CCCC",            "FFFF XXXX YYYY"]

    assert act_seg_ner._extract_acts(text, pred) == alvo
