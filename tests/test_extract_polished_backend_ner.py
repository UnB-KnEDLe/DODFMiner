import os
import joblib
import pytest
import numpy as np
from unittest.mock import patch
from dodfminer.extract.polished.backend.ner import ActNER

def test_act_ner_backend_fallback():
    act = ActNER()
    act._name = ""
    act._backend = 'ner'
    act._model = act._load_model()
    assert act._backend == 'regex'

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
