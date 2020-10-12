import os
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch
from dodfminer.extract.polished.acts.base import Atos

rule_dict = {
    "numeros": r"([0-9]+)",
    "capitalizado": r"([A-Z][a-z]+)",
    "nao_encontra": "khalil"
}
rule_prop = r"(MENSAGEM:)([^.]*)"
props = ["Tipo", "Numeros", "Capitalizado", "Não Encontra"]
valid_file = ""+os.path.dirname(__file__)+"/support/valid.txt"

text = "fghngfnfgnfgnfgnrr MENSAGEM: O Renato testa esse codigo 1232 vezes por dia. qeqcnoecqucqpwxqrthrweqqeprto MENSAGEM: O Joao testa esse codigo 2 vezes por dia. wsfhsn wenrwermrkne MENSAGEM: O Lucas testa esse codigo 0 vezes por dia. efwefwefwfwefwetrynyujuju"
act =  [' O Renato testa esse codigo 1232 vezes por dia', ' O Joao testa esse codigo 2 vezes por dia', ' O Lucas testa esse codigo 0 vezes por dia']

res_act = [{'tipo_ato': 'Aposentadoria', 'numeros': '1232', 'capitalizado': 'Renato', 'nao_encontra': np.nan}, {'tipo_ato': 'Aposentadoria', 'numeros': '2', 'capitalizado': 'Joao', 'nao_encontra': np.nan}, {'tipo_ato': 'Aposentadoria', 'numeros': '0', 'capitalizado': 'Lucas', 'nao_encontra': np.nan}]


# Wrong Init Type
@patch.object(Atos, '_act_name', return_value="Aposentadoria")
@patch.object(Atos, '_props_names', return_value=props)
@patch.object(Atos, '_rule_for_inst', return_value=rule_prop)
@patch.object(Atos, '_prop_rules', return_value=rule_dict)
def test_act_base_invalid_file(test_act_name, test_return_value,
                               test_rules_inst, test_rules_prop):
    file = ""+os.path.dirname(__file__)+"/support/invalid.pdf"
    act = Atos(file,'regex')
    assert act._file_name == None
    assert act._text == file

@patch.object(Atos, '_act_name', return_value="Aposentadoria")
@patch.object(Atos, '_props_names', return_value=props)
@patch.object(Atos, '_rule_for_inst', return_value=rule_prop)
@patch.object(Atos, '_prop_rules', return_value=rule_dict)
def test_act_non_existiong_backend(test_act_name, test_return_value,
                                   test_rules_inst, test_rules_prop):
    ato = Atos(valid_file, 'lol')
    assert ato._backend == 'regex'

@patch.object(Atos, '_act_name', return_value="Aposentadoria")
@patch.object(Atos, '_props_names', return_value=props)
@patch.object(Atos, '_rule_for_inst', return_value=rule_prop)
@patch.object(Atos, '_prop_rules', return_value=rule_dict)
def test_act_backend_fallback(test_act_name, test_return_value,
                                   test_rules_inst, test_rules_prop):
    ato = Atos(valid_file, 'ner')
    assert ato._backend == 'regex'

# Wrong Init
@patch.object(Atos, '_act_name', return_value="Aposentadoria")
@patch.object(Atos, '_props_names', return_value=props)
@patch.object(Atos, '_rule_for_inst', return_value=rule_prop)
def test_no_overwrite_1(test_act_name, test_return_value,
                        test_rules_inst):
    with pytest.raises(Exception):
        Atos(valid_file,'regex')

@patch.object(Atos, '_act_name', return_value="Aposentadoria")
@patch.object(Atos, '_props_names', return_value=props)
@patch.object(Atos, '_prop_rules', return_value=rule_dict)
def test_no_overwrite_2(test_act_name, test_return_value,
                        test_rules_prop):
    with pytest.raises(Exception):
        Atos(valid_file,'regex')

@patch.object(Atos, '_act_name', return_value="Aposentadoria")
@patch.object(Atos, '_rule_for_inst', return_value=rule_prop)
@patch.object(Atos, '_prop_rules', return_value=rule_dict)
def test_no_overwrite_3(test_act_name, test_rules_inst,
                        test_rules_prop):
    with pytest.raises(Exception):
        Atos(valid_file,'regex')

@patch.object(Atos, '_props_names', return_value=props)
@patch.object(Atos, '_rule_for_inst', return_value=rule_prop)
@patch.object(Atos, '_prop_rules', return_value=rule_dict)
def test_no_overwrite_4(test_return_value, test_rules_inst,
                        test_rules_prop):
    with pytest.raises(Exception):
        Atos(valid_file,'regex')

def test_no_overwrite_5():
    with pytest.raises(Exception):
        Atos(valid_file,'regex')


@pytest.fixture
@patch.object(Atos, '_act_name', return_value="Aposentadoria")
@patch.object(Atos, '_props_names', return_value=["Numeros", "Capitalizado", "Não Encontra"])
@patch.object(Atos, '_rule_for_inst',
              return_value=r"(MENSAGEM:)([^.]*)")
@patch.object(Atos, '_prop_rules',return_value={
    "numeros": r"([0-9]+)",
    "capitalizado": r"([A-Z][a-z]+)",
    "nao_encontra": "khalil"
})
def act_base_regex(test_act_name, test_return_value,
                   test_rules_inst, test_rules_prop):
    atos = Atos(valid_file,'regex')
    atos._name = "Aposentadoria"
    return atos

def test_act_base_name(act_base_regex):
    assert act_base_regex.name == "Aposentadoria"

def test_act_base_name_attr(act_base_regex):
    assert act_base_regex._name == "Aposentadoria"

def test_act_file_name(act_base_regex):
    assert act_base_regex._file_name == valid_file

def test_act_base_raw_acts_regex(act_base_regex):
    act_base_regex._backend = 'regex'
    act_base_regex._text = text
    assert act_base_regex._extract_instances() == act

def test_act_base_raw_acts_ner(act_base_regex):
    act_base_regex._backend = 'ner'
    act_base_regex._text = text
    assert act_base_regex._extract_instances() == act

def test_act_base_raw_acts_error(act_base_regex):
    act_base_regex._backend = 'lol'
    act_base_regex._text = text
    with pytest.raises(Exception):
        act_base_regex._extract_instances()

def test_act_base_props_regex(act_base_regex):
    act_base_regex._backend = 'regex'
    act_base_regex._raw_acts = act
    print(act_base_regex._acts)
    assert act_base_regex._extract_props() == res_act

def test_act_base_build_dataframes(act_base_regex):
    act_base_regex._backend = 'regex'
    act_base_regex._acts = res_act
    act_base_regex._columns = props
    res_df = pd.DataFrame(res_act)
    res_df.columns = props

    assert act_base_regex._build_dataframe().equals(res_df)

def test_act_base_build_dataframes_empty(act_base_regex):
    act_base_regex._backend = 'regex'
    res_df = pd.DataFrame()
    assert act_base_regex._build_dataframe().equals(res_df)

def test_act_base_props_error(act_base_regex):
    act_base_regex._backend = 'lol'
    act_base_regex._raw_acts = act
    with pytest.raises(Exception):
        act_base_regex._extract_props()
