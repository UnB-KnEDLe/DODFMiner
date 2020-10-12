import pytest
import numpy as np
from unittest.mock import patch
from dodfminer.extract.polished.backend.regex import ActRegex

@pytest.fixture
@patch.object(ActRegex, '_rule_for_inst',
              return_value=r"(MENSAGEM:)([^.]*)")
@patch.object(ActRegex, '_prop_rules',return_value={
    "numeros": r"([0-9]+)",
    "capitalizado": r"([A-Z][a-z]+)",
    "nao_encontra": "khalil"
})
def act_regex(test_rule_for_inst, test_prop_rules):
    act =  ActRegex()
    act._acts_str = []
    return act

def test_act_regex_flags(act_regex):
    assert act_regex._flags == 0

def test_act_regex_rules(act_regex):
    assert act_regex._rules == {
    "numeros": r"([0-9]+)",
    "capitalizado": r"([A-Z][a-z]+)",
    "nao_encontra": "khalil"
    }

def test_act_regex_inst_rule(act_regex):
    assert act_regex._inst_rule == r"(MENSAGEM:)([^.]*)"

def test_act_regex_regex_props(act_regex):
    act_regex._name = "Teste"
    act_raw = "MENSAGEM: O Renato testa esse codigo 1232 vezes por dia."
    act = act_regex._regex_props(act_raw)
    assert act == {"tipo_ato": "Teste", "numeros": "1232", "capitalizado": "Renato", "nao_encontra": np.nan}


def test_act_regex_regex_instances(act_regex):
    act_regex._text = "fghngfnfgnfgnfgnrr MENSAGEM: O Renato testa esse codigo 1232 vezes por dia. qeqcnoecqucqpwxqrthrweqqeprto MENSAGEM: O Joao testa esse codigo 2 vezes por dia. wsfhsn wenrwermrkne MENSAGEM: O Lucas testa esse codigo 0 vezes por dia. efwefwefwfwefwetrynyujuju"
    act_regex.acts_str = []
    act = act_regex._regex_instances()
    assert act == [' O Renato testa esse codigo 1232 vezes por dia', ' O Joao testa esse codigo 2 vezes por dia', ' O Lucas testa esse codigo 0 vezes por dia']

def test_act_regex_find_prop_value(act_regex):
    res = act_regex._find_prop_value("(de)", "String de teste")
    assert res == ('de',)

def test_act_regex_find_multiple_prop_value(act_regex):
    res = act_regex._find_prop_value("(de) (teste)", "String de teste")
    assert res == ('de', 'teste',)

def test_act_regex_dont_find_prop_value(act_regex):
    res = act_regex._find_prop_value("dos", "String de teste")
    assert res is np.nan

@patch.object(ActRegex, '_prop_rules')
def test_no_rule_inst_act_regex(test_prop_rules):
    with pytest.raises(Exception):
        ActRegex()

@patch.object(ActRegex, '_rule_for_inst')
def test_no_prop_rule_act_regex(test_rule_for_inst):
    with pytest.raises(Exception):
        ActRegex()

def test_not_implemented_functions_act_regex():
    with pytest.raises(Exception):
        ActRegex()
