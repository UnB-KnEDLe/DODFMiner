import os
import joblib
import pytest
import numpy as np
from unittest.mock import patch
from dodfminer.extract.polished.backend.ner import ActNER

@pytest.fixture
@patch.object(ActNER, '_load_model',
              return_value=joblib.load(""+os.path.dirname(__file__)+"/support/test_model.pkl"))

def act_ner_with_model(mock_model):
    act = ActNER()
    act._name = ""
    act._backend = 'ner'
    return act

def test_act_ner_backend_ner(act_ner_with_model):
    assert act_ner_with_model._backend == 'ner'

def test_act_ner_preprocess(act_ner_with_model):
    # Caso 1 (Sentenca inventada)
    str1 = "hoje, eu vou. amanha, talvez. pode ser\n que sim; pode\n ser que nao"
    str2 = ["hoje", ",", "eu", "vou", ".", "amanha", ",", "talvez", ".", "pode", "ser", "que", "sim", ";", "pode", "ser", "que", "nao"]
    test1= (act_ner_with_model._preprocess(str1)==str2)
    # Caso 2 (Sentenca de um DODF)
    str1 = "Art. 4o Validar os atos escolares praticados pela instituicao educacional, a contar de 1o de\njaneiro de 2012 ate a data de publicacao da portaria oriunda do presente parec e r. "
    str2 = ["Art", ".", "4o", "Validar", "os", "atos", "escolares", "praticados", "pela", "instituicao", "educacional", ",", "a", "contar", "de", "1o", "de", "janeiro", "de", "2012", "ate", "a", "data", "de", "publicacao", "da", "portaria", "oriunda", "do", "presente", "parec", "e", "r", "."]
    test2= (act_ner_with_model._preprocess(str1)==str2)
    assert test1 and test2

def test_act_ner_get_features(act_ner_with_model):

    list_1 = ["Art", ".", "4", "Validar", "ATOS", "."]
    features_1 = [{'word': 'art',
                'capital_letter': True,
                'all_capital': False,
                'isdigit': False,
                'word_before': 'art',
                'word_after:': '.',
                'BOS': True,
                'EOS': False
                },
                {'word': '.',
                'capital_letter': False,
                'all_capital': False,
                'isdigit': False,
                'word_before': 'art',
                'word_after:': '4',
                'BOS': False,
                'EOS': False
                },
                {'word': '4',
                'capital_letter': False,
                'all_capital': False,
                'isdigit': True,
                'word_before': '.',
                'word_after:': 'validar',
                'BOS': False,
                'EOS': False
                },
                {'word': 'validar',
                'capital_letter': True,
                'all_capital': False,
                'isdigit': False,
                'word_before': '4',
                'word_after:': 'atos',
                'BOS': False,
                'EOS': False
                },
                {'word': 'atos',
                'capital_letter': True,
                'all_capital': True,
                'isdigit': False,
                'word_before': 'validar',
                'word_after:': '.',
                'BOS': False,
                'EOS': False
                },
                {'word': '.',
                'capital_letter': False,
                'all_capital': False,
                'isdigit': False,
                'word_before': 'atos',
                'word_after:': '.',
                'BOS': False,
                'EOS': True
                }]
    assert features_1 == act_ner_with_model._get_features(list_1)

def test_act_ner_prediction(act_ner_with_model):
    sentence    = "matricula 190133743 joao souza artigo 5o data 03/12/1901 cargo professor"
    # Step-by-step execution of _prediction()
    sent = act_ner_with_model._preprocess(sentence)
    feats = act_ner_with_model._get_features(sent)
    predictions = act_ner_with_model._model.predict_single(feats)
    entities_predicted_StepByStep = act_ner_with_model._predictions_dict(sent, predictions)
    # Direct execution of _prediction()
    entities_predicted_at_once = act_ner_with_model._prediction(sentence)

    # Evaluating _model.predict_single()
    test1 = True
    for prediction in predictions:
        if prediction not in act_ner_with_model._model.classes_:
            test1 = False
    # Check if step-by-step is equivalent to at_once execution
    test2 = entities_predicted_at_once == entities_predicted_StepByStep
    assert test1 and test2

def test_act_ner_predictions_dict(act_ner_with_model):
    prediction = ["B-matricula", "I-matricula", "B-Nome do Servidor", "I-Nome do Servidor", "B-fundamento legal do abono de permanencia", "I-fundamento legal do abono de permanencia", "B-Vigencia", "I-Vigencia", "B-Cargo Efetivo", "I-Cargo Efetivo"]
    sentence    = ["matricula"  , "190133743"  , "joao"              , "souza"             , "artigo"                                    , "5o"                                        ,  "data"     , "03/12/1901", "cargo"          , "professor"]
    entidades = {
        'Tipo do Ato': '',
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
    assert entidades == act_ner_with_model._predictions_dict(sentence, prediction)
