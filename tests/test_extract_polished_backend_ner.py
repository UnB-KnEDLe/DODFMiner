# pylint: disable=protected-access

import os
from unittest.mock import patch
import joblib
import pytest
import numpy as np
from dodfminer.extract.polished.backend.ner import ActNER


@pytest.fixture(name='act_ner_with_model')
@patch.object(ActNER, '_load_model',
              return_value=joblib.load(""+os.path.dirname(__file__)+"/support/test_model.pkl"))
def fixture_act_ner_with_model(_):
    act = ActNER()
    act._name = ""
    act._backend = 'ner'
    return act

def test_act_ner_backend_ner(act_ner_with_model):
    assert act_ner_with_model._backend == 'ner'


def test_act_ner_preprocess(act_ner_with_model):
    sentence = "teste    com   pala-\nvras."
    assert act_ner_with_model._preprocess(sentence) == 'teste com palavras.'

def test_act_ner_limits(act_ner_with_model):
    sentence = "teste com palavras.123"
    assert act_ner_with_model._limits(sentence) == [0, 6, 10, 18, 19]

def test_act_ner_split_sentence(act_ner_with_model):
    # Caso 1 (Sentenca inventada)
    str1 = "hoje, eu vou. amanha, talvez. pode ser que sim; pode ser que nao"
    str2 = ["hoje", ",", "eu", "vou", ".", "amanha", ",", "talvez", ".",
            "pode", "ser", "que", "sim", ";", "pode", "ser", "que", "nao"]
    test1 = (act_ner_with_model._split_sentence(str1) == str2)
    # Caso 2 (Sentenca de um DODF)
    str1 = "Art. 4o Validar os atos escolares praticados pela instituicao educacional, a contar de 1o de janeiro de 2012 ate " + \
        "a data de publicacao da portaria oriunda do presente parec e r. "
    str2 = [
        "Art",
        ".",
        "4",
        "o",
        "Validar",
        "os",
        "atos",
        "escolares",
        "praticados",
        "pela",
        "instituicao",
        "educacional",
        ",",
        "a",
        "contar",
        "de",
        "1",
        "o",
        "de",
        "janeiro",
        "de",
        "2012",
        "ate",
        "a",
        "data",
        "de",
        "publicacao",
        "da",
        "portaria",
        "oriunda",
        "do",
        "presente",
        "parec",
        "e",
        "r",
        "."
    ]
    test2 = (act_ner_with_model._split_sentence(str1) == str2)
    assert test1 and test2

def test_act_ner_get_base_feat(act_ner_with_model):
    feat = {
        'word': 'teste001',
        'is_title': False,
        'is_upper': False,
        'num_digits': '3',
    }
    assert act_ner_with_model._get_base_feat("teste001") == feat

def test_act_ner_add_base_feat(act_ner_with_model):
    features = {'': 1}
    sentence = ["Teste01", ","]
    index = 1
    prefix = '+1:'

    feat_target = {'': 1, '+1:word': ',', '+1:is_title': False, '+1:is_upper': False, '+1:num_digits': '0'}

    act_ner_with_model._add_base_feat(features, sentence, index, prefix)

    assert features == feat_target


def test_act_ner_get_features(act_ner_with_model):

    list_1 = ["Art", ".", "4", "-", "ATOS"]
    features_1 = [
        {
            'bias': 1.0,
            'text_position': 0.0,
            'word': 'art', 'is_title': True, 'is_upper': False, 'num_digits': '0',
            '+1:word': '.', '+1:is_title': False, '+1:is_upper': False, '+1:num_digits': '0',
            '+2:word': '4', '+2:is_title': False, '+2:is_upper': False, '+2:num_digits': '1',
            '+3:word': '-', '+3:is_title': False, '+3:is_upper': False, '+3:num_digits': '0',
            '+4:word': 'atos', '+4:is_title': False, '+4:is_upper': True, '+4:num_digits': '0',
        },
        {
            'bias': 1.0,
            'text_position': 0.2,
            '-1:word': 'art', '-1:is_title': True, '-1:is_upper': False, '-1:num_digits': '0',
            'word': '.', 'is_title': False, 'is_upper': False, 'num_digits': '0',
            '+1:word': '4', '+1:is_title': False, '+1:is_upper': False, '+1:num_digits': '1',
            '+2:word': '-', '+2:is_title': False, '+2:is_upper': False, '+2:num_digits': '0',
            '+3:word': 'atos', '+3:is_title': False, '+3:is_upper': True, '+3:num_digits': '0',
        },
        {
            'bias': 1.0,
            'text_position': 0.4,
            '-2:word': 'art', '-2:is_title': True, '-2:is_upper': False, '-2:num_digits': '0',
            '-1:word': '.', '-1:is_title': False, '-1:is_upper': False, '-1:num_digits': '0',
            'word': '4', 'is_title': False, 'is_upper': False, 'num_digits': '1',
            '+1:word': '-', '+1:is_title': False, '+1:is_upper': False, '+1:num_digits': '0',
            '+2:word': 'atos', '+2:is_title': False, '+2:is_upper': True, '+2:num_digits': '0',
        },
        {
            'bias': 1.0,
            'text_position': 0.6,
            '-3:word': 'art', '-3:is_title': True, '-3:is_upper': False, '-3:num_digits': '0',
            '-2:word': '.', '-2:is_title': False, '-2:is_upper': False, '-2:num_digits': '0',
            '-1:word': '4', '-1:is_title': False, '-1:is_upper': False, '-1:num_digits': '1',
            'word': '-', 'is_title': False, 'is_upper': False, 'num_digits': '0',
            '+1:word': 'atos', '+1:is_title': False, '+1:is_upper': True, '+1:num_digits': '0',
        },
        {
            'bias': 1.0,
            'text_position': 0.8,
            '-4:word': 'art', '-4:is_title': True, '-4:is_upper': False, '-4:num_digits': '0',
            '-3:word': '.', '-3:is_title': False, '-3:is_upper': False, '-3:num_digits': '0',
            '-2:word': '4', '-2:is_title': False, '-2:is_upper': False, '-2:num_digits': '1',
            '-1:word': '-', '-1:is_title': False, '-1:is_upper': False, '-1:num_digits': '0',
            'word': 'atos', 'is_title': False, 'is_upper': True, 'num_digits': '0',
        }
    ]
    assert features_1 == act_ner_with_model._get_features(list_1)


def test_act_ner_prediction(act_ner_with_model):
    sentence = "matricula 190133743 joao souza artigo 5o data 03/12/1901 cargo professor"
    # Step-by-step execution of _prediction()
    sent = act_ner_with_model._preprocess(sentence)
    sent_list = act_ner_with_model._split_sentence(sent)
    feats = act_ner_with_model._get_features(sent_list)
    predictions = act_ner_with_model._model.predict_single(feats)
    entities_predicted_step_by_step = act_ner_with_model._predictions_dict(
        sent, predictions)
    # Direct execution of _prediction()
    entities_predicted_at_once = act_ner_with_model._prediction(sentence)

    # Evaluating _model.predict_single()
    test1 = True
    for prediction in predictions:
        if prediction not in act_ner_with_model._model.classes_:
            test1 = False
    # Check if step-by-step is equivalent to at_once execution
    test2 = entities_predicted_at_once == entities_predicted_step_by_step
    assert test1 and test2


def test_act_ner_predictions_dict(act_ner_with_model):
    prediction = ["B-matricula", "I-matricula", "B-Nome do Servidor", "I-Nome do Servidor", "B-fundamento legal do abono de permanencia",
                  "I-fundamento legal do abono de permanencia", "I-fundamento legal do abono de permanencia",
                  "B-Vigencia", "I-Vigencia", "I-Vigencia", "I-Vigencia", "I-Vigencia", "I-Vigencia",
                  "B-Cargo Efetivo", "I-Cargo Efetivo"]
    sentence = "matricula 190133743 joao souza artigo 5o data 03/12/1901 cargo professor"

    entidades = {
        'matricula': "matricula 190133743",
        'Nome do Servidor': "joao souza",
        'fundamento legal do abono de permanencia': "artigo 5o",
        'Vigencia': "data 03/12/1901",
        'Cargo Efetivo': "cargo professor",
        'Classe': np.nan,
        'padrao': np.nan,
        'Quadro pessoal permanente ou Suplementar': np.nan,
        'Matricula SIAPE': np.nan,
        'Processo GDF/SEI': np.nan,
        'orgao': np.nan
    }

    assert entidades == act_ner_with_model._predictions_dict(
        sentence, prediction)
