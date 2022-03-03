# pylint: disable=protected-access

import os
import re
import pytest
import sklearn_crfsuite

from dodfminer.extract.polished.acts.aposentadoria import Retirements, RetAposentadoria
from dodfminer.extract.polished.acts.nomeacao import NomeacaoComissionados, NomeacaoEfetivos
from dodfminer.extract.polished.acts.exoneracao import Exoneracao, ExoneracaoEfetivos
from dodfminer.extract.polished.acts.reversoes import Revertions
from dodfminer.extract.polished.acts.abono import AbonoPermanencia
from dodfminer.extract.polished.acts.substituicao import Substituicao
from dodfminer.extract.polished.acts.cessoes import Cessoes
from dodfminer.extract.polished.acts.contrato import Contratos
from dodfminer.extract.polished.acts.sem_efeito_aposentadoria import SemEfeitoAposentadoria

file = ""+os.path.dirname(__file__)+"/support/valid.txt"
file_2 = ""+os.path.dirname(__file__)+"/support/valid_2.txt"


@pytest.fixture(name='act_cont')
def fixture_act_cont():
    return Contratos(file_2, 'regex')


def test_contrato_backend(act_cont):
    assert act_cont._backend == "regex"


def test_contrato_name(act_cont):
    assert act_cont._name == "Contrato"
    assert act_cont.name == "Contrato"
    assert act_cont._act_name() == "Contrato"


def test_contrato_flags(act_cont):
    assert act_cont._regex_flags() == re.IGNORECASE


def test_contrato_prop_names(act_cont):
    assert act_cont._props_names() == ["Tipo do Ato", "CONTRATO", "PROCESSO", "PARTES", "OBJETO", "VALOR",
                                       "LEI_ORC.", "UNI_ORC.", "PROG_TRAB.", "NAT_DESP.", "NOTA_EMP.", "DATA_ASS.", "SIGNATARIOS", "VIGENCIA"]


def test_contrato_rule(act_cont):
    assert act_cont._rule_for_inst(
    ) == r"()" + r"(EXTRATO D[O|E] CONTRATO\s[\s\S]*?" + r"<EOB>)"


def test_contrato_prop_rules_names(act_cont):
    assert list(act_cont._prop_rules()) == ["CONTRATO", "PROCESSO", "PARTES", "OBJETO", "VALOR", "LEI_ORC.",
                                            "UNI_ORC.", "PROG_TRAB.", "NAT_DESP.", "NOTA_EMP.", "DATA_ASS.", "SIGNATARIOS", "VIGENCIA"]


def test_contrato_prop_rules_rules(act_cont):
    assert list(act_cont._prop_rules().values()) == [
        r"EXTRATO D[E|O] CONTRATO[\s\S]*?(\d+\/\d{4})",
        r"[P|p][R|r][O|o][C|c][E|e][S|s][S|s][O|o][\s\S].*?(\d*[^;|,|a-zA-Z]*)",
        r"Partes:[\s\S].*?([^;|.]*)|PARTES:[\s\S].*?([^;|.]*)|Contratante:[\s\S].*?([^;|.]*)|" +
        r"Contratantes:[\s\S].*?([^;|.]*)|CONTRATANTE:[\s\S].*?([^;|.]*)|CONTRATANTES:[\s\S].*?([^;|.]*)",
        r"[O|o][B|b][J|j][E|e][T|t][O|o][\s\S].*?(\d*[^;|.|]*)",
        r"[v|V][a|A][l|L][o|O][r|R].*?[\s\S].*?([R$ \d\.]*,\d{2})",
        r"[L|l][E|e][I|i][\s\S][o|O][r|R][c|C|ç|Ç][a|A][m|M][e|E][n|N][t|T][a|A|á|Á][r|R][i|I][a|A].*?" +
        r"[\s\S].*?([N|n][o|O|º|°] \d+.\d+\/d{4}|[N|n][o|O|º|°] \d+.\d+)",
        r"[u|U][n|N][i|I][d|D][a|A][d|D][e|E][\s\S][o|O][r|R][c|C|ç|Ç][a|A][m|M][e|E][n|N][t|T][a|A|á|Á][r|R][i|I][a|A].*?[\s\S]" +
        r".*?(\d+.\d+)|[U][.][O].*?[\s\S].*?(\d+.\d+)|[U][O].*?[\s\S].*?(\d+.\d+)",
        r"[P|p][R|r][O|o][g|G][r|R][a|A][m|M][a|A][\s|\S][d|D][e|E|O|o|A|a][\s|\S][T|t][R|r][A|a][B|b][A|a][L|l][H|h][O|o].*?" +
        r"[:|;|[\s\S].*?(\d*[^;|,|–|(|Nat|Not|Uni|Ent]*)",
        r"[N|n][a|A][t|T][u|U][r|R][e|E][z|Z][a|A][\s\S][D|d][e|E|a|A][\s\S][d|D][e|E][s|S][p|P][e|E][s|S][a|A]" +
        r"[:|\s|\S][\s\S].*?(\d*[^;|,|–|(|a-zA-Z]*)",
        r"(\d+NE\d+)",
        r"[A|a][S|s][S|s][I|i][N|n][A|a][T|t][U|u][R|r][A|a]:.*?[\s\S](\d{2}\/\d{2}\/\d{4}|\d{2}[\s\S]\w+[\s\S]\w+[\s\S]\w+[\s\S]\d{4})",
        r"Signat[á|a]rios:([^;|.]*)|SIGNAT[Á|A]RIOS:([^;|.]*)|Assinantes:([^;|.]*)|ASSINANTES:([^;|.]*)",
        r"Vig[e|ê]ncia:[\s\S]([^;|.]*)|VIG[E|Ê]NCIA:[\s\S]([^;|.]*)",
    ]


def test_act_contrato_consistence_rule(act_cont):
    assert len(act_cont._props_names())-1 == len(act_cont._prop_rules())


def test_act_contrato_ner():
    act = Contratos(file, 'ner')
    assert isinstance(act._load_model(), sklearn_crfsuite.estimator.CRF)

#
#
#
#
#


@pytest.fixture(name='act_ret')
def fixture_act_ret():
    return Retirements(file, 'regex')


def test_retirement_backend(act_ret):
    assert act_ret._backend == "regex"


def test_retirement_name(act_ret):
    assert act_ret._name == "Aposentadoria"
    assert act_ret.name == "Aposentadoria"
    assert act_ret._act_name() == "Aposentadoria"


def test_retirement_flags(act_ret):
    assert act_ret._regex_flags() == re.IGNORECASE


def test_retirement_prop_names(act_ret):
    assert act_ret._props_names() == [
        'Ato',
        'Processo',
        'Nome_ato',
        'Cod_matricula_ato',
        'Cargo',
        'Classe',
        'Padrao',
        'Quadro',
        'Fund_legal',
        'Empresa_ato',
    ]


def test_retirement_rule(act_ret):
    assert act_ret._rule_for_inst(
    ) == r"(APOSENTAR[^-]|CONCEDER,\sAPOSENTADORIA|CONCEDER\sAPOSENTADORIA,?\s?)([\s\S]*?(?<!lei)\s(?:[0-9|\s]*" + \
        r"?[.|-]\s?)+?[0-9|\s]*/\s?[0-9|\s]*-?\s?[0-9|\s]*[.|,])"


def test_retirement_prop_rules_names(act_ret):
    assert list(act_ret._prop_rules()) == [
        "processo_SEI",
        "nome",
        "matricula",
        # "tipo_ret",
        "cargo_efetivo",
        "classe",
        "padrao",
        "quadro",
        "fundamento_legal",
        "orgao",
        # "vigencia",
        # "matricula_SIAPE"
    ]


def test_retirement_prop_rules_rules(act_ret):
    assert list(act_ret._prop_rules().values()) == [
        r"(?<!lei)\s((?:[0-9|\s]*?[.|-]\s?)+?[0-9|\s]*/\s?[0-9|\s]*-?\s?[0-9|\s]*)[.|,]",
        r"\s([^,]*?),\smatricula",
        r"matricula\s?n?o?\s([\s\S]*?)[,|\s]",
        # r"",
        r"Cargo de([\s\S]*?)\,",
        r"[C|c]lasse\s([\s\S]*?)\,",
        r"[p|P]adr[a|ã]o\s([\s\S]*?),",
        r"d?[e|a|o]?(Quadro[\s\S]*?)[,|;|.]",
        r"nos\stermos\sdo\s[a|A]rtigo([\s\S]*?),\sa?\s",
        r"Lotacao:|Quadro\sde\sPessoal\sd[a|e|o]([\s\S]*?)[.|,]",
        # r"",
        # r"[S|s][I|i][A|a][P|p][E|e]\s[N|n]?[o|O]?\s([\s\S]*?)[,| | .]"
    ]


def test_act_retirement_consistence_rule(act_ret):
    assert len(act_ret._props_names())-1 == len(act_ret._prop_rules())


def test_act_retirement_ner():
    act = Retirements(file, 'ner')
    assert isinstance(act._load_model(), sklearn_crfsuite.estimator.CRF)

#
#
#
#
#


@pytest.fixture(name='act_retapos')
def fixure_act_retapos():
    return RetAposentadoria(file, 'regex')


def test_retretirement_backend(act_retapos):
    assert act_retapos._backend == "regex"


def test_retretirement_name(act_retapos):
    assert act_retapos._name == "Retificações de Aposentadoria"
    assert act_retapos.name == "Retificações de Aposentadoria"
    assert act_retapos._act_name() == "Retificações de Aposentadoria"


def test_retretirement_flags(act_retapos):
    assert act_retapos._regex_flags() == re.IGNORECASE


def test_retretirement_prop_names(act_retapos):
    assert act_retapos._props_names() == ["Tipo do Ato", "Tipo de Documento", "Número do documento",
                                          "Data do documento ", "Número do DODF", "Data do DODF",
                                          "Página do DODF", "Nome do Servidor", "Matrícula", "Cargo",
                                          "Classe", "Padrao", "Matricula SIAPE",
                                          "Informação Errada", "Informação Corrigida"]


def test_retretirement_rule(act_retapos):
    assert act_retapos._rule_for_inst(
    ) == r"(RETIFICAR,\s)(.*?ato\sque\sconcedeu\saposentadoria[\s\S]*?\.\n)"


def test_retretirement_prop_rules_names(act_retapos):
    assert list(act_retapos._prop_rules()) == [
        "tipo_documento",
        "numero_documento",
        "data_documento",
        "numero_dodf",
        "data_dodf",
        "pagina_dodf",
        "nome",
        "matricula",
        "cargo_efetivo",
        "classe",
        "padrao",
        "matricula_SIAPE",
        "informacao_errada",
        "informacao_corrigida"]


def test_retretirement_prop_rules_rules(act_retapos):
    assert list(act_retapos._prop_rules().values()) == [
        r"^n[a|o]\s([\s\S]*?),?\s?(?:[0-9]*?),?\sde\s(?:[0-9]*?[/|.][0-9]*?[/|.][0-9]*?|,)",
        r"n[a|o]\s(?:[\s\S]*?),?\s?([0-9]*?),?\sde\s(?:[0-9]*?[/|.][0-9]*?[/|.][0-9]*?|,)",
        r"n[a|o]\s(?:[\s\S]*?),?\s?(?:[0-9]*?),?\sde\s([0-9]*?[/|.][0-9]*?[/|.][0-9]*?),\s",
        r"dodf[\s\S]*?([0-9]*?),",
        r"dodf[\s\S]*?(?:[0-9]*?)([0-9]*?[/|.][0-9]*?[/|.][0-9]*?)[,|\s]",
        r"",
        r"\sa\s([^,]*?),\smatricula",
        r"matricula\s?n?o?\s([\s\S]*?-[\s\S]*?)[,]",
        r"(?:Cargo|Carreira)\sde([\s\S]*?)\,",
        r"(?:([^,]*?)\sclasse,)?(?(1)|classe\s([\s\S]*?),)",
        r"[p|P]adr[a|ã]o\s([\s\S]*?),",
        r"siape\sn?o?\s([\s\S]*?)[,| | .]",
        r"\sle[,|:|;]\s?([\s\S]*?),?\sleia[\s\S]*?[,|:|;]\s(?:[\s\S]*?)[.]\s",
        r"\sle[,|:|;]\s?(?:[\s\S]*?),?\sleia[\s\S]*?[,|:|;]\s([\s\S]*?)[.]\s"
    ]


def test_act_retretirement_consistence_rule(act_retapos):
    assert len(act_retapos._props_names())-1 == len(act_retapos._prop_rules())


def test_act_retretirement_ner():
    act = RetAposentadoria(file, 'ner')
    assert act._backend == 'regex'

#
#
#
#
#


@pytest.fixture(name='act_abono')
def fixture_act_abono():
    return AbonoPermanencia(file, 'regex')


def test_abono_backend(act_abono):
    assert act_abono._backend == "regex"


def test_abono_name(act_abono):
    assert act_abono._name == "Abono de Permanência"
    assert act_abono.name == "Abono de Permanência"
    assert act_abono._act_name() == "Abono de Permanência"


def test_abono_flags(act_abono):
    assert act_abono._regex_flags() == re.IGNORECASE | re.MULTILINE


def test_abono_prop_names(act_abono):
    assert act_abono._props_names() == [
        'Tipo do Ato',
        'Nome',
        'Matricula',
        'Cargo_efetivo',
        'Classe',
        'Padrao',
        'Quadro',
        'Fundamento_legal',
        'Orgao',
        'Processo_sei',
        'Vigencia',
        'Matricula_siape',
        # Problematicos que estão no modelos ner
        'Cargo',
        'Lotacao'
    ]


def test_abono_rule(act_abono):
    assert act_abono._rule_for_inst(
    ) == r"(Abono\sDE\sPERMANENCIA\s[(ao|equiva)][\s\S]*?)\s([\s\S]*?\d+\s*[\.|\-]\s*\d+\s*\/\s*\d+\s*\-\s*\d+)"


def test_abono_prop_rules_names(act_abono):
    assert list(act_abono._prop_rules()) == [
        "nome",
        "matricula",
        "cargo_efetivo",
        "classe",
        "padrao",
        "quadro",
        "fundamento_legal_abono_permanencia",
        "orgao",
        "processo_SEI",
        "vigencia",
        "matricula_SIAPE",
        'cargo',
        'lotacao'
    ]


def test_abono_prop_rules_rules(act_abono):
    assert list(act_abono._prop_rules().values()) == [
        r"\s([^,]*?),\smatricula",
        r"matricula\s?n?o?\s([\s\S]*?)[,|\s]",
        r"Cargo\s[d|D]?[e|E]?\s([\s\S]*?),",
        r"[C|c]lasse\s([\s\S]*?),",
        r"[p|P]adr[a|ã]o\s([\s\S]*?),",
        r"d?[e|a|o]?(Quadro[\s\S]*?)[,|;|.]",
        r"nos\stermos\sdo\s([\s\S]*?),\sa?\s",
        r"Lotacao: ([\s\S]*?)[.]",
        r"Processo SEI: ([\s\S]*?)\.\n",
        r"a contar de ([\s\S]*?)\,",
        r"[S|s][I|i][A|a][P|p][E|e]\s[N|n]?[o|O]?\s([\s\S]*?)[,| | .]",
        r'',
        r''
    ]


def test_act_abono_consistence_rule(act_abono):
    assert len(act_abono._props_names())-1 == len(act_abono._prop_rules())


def test_act_abono_ner():
    act = AbonoPermanencia(file, 'ner')
    assert isinstance(act._load_model(), sklearn_crfsuite.estimator.CRF)

#
#
#
#
#


@pytest.fixture(name='act_exoneracao')
def fixture_act_exoneracao():
    return Exoneracao(file, 'regex')


def test_exoneracao_backend(act_exoneracao):
    assert act_exoneracao._backend == "regex"


def test_exoneracao_name(act_exoneracao):
    assert act_exoneracao._name == "Exoneração"
    assert act_exoneracao.name == "Exoneração"
    assert act_exoneracao._act_name() == "Exoneração"


def test_exoneracao_flags(act_exoneracao):
    assert act_exoneracao._regex_flags() == 0


def test_exoneracao_prop_names(act_exoneracao):
    assert act_exoneracao._props_names() == [
        'Tipo do Ato',
        'Nome',
        'Matricula',
        'Simbolo',
        'Cargo_comissionado',
        'Hierarquia_lotacao',
        'Orgao',
        'Vigencia',
        'Carreira',
        'Fundamento_legal',
        'A_pedido_ou_nao',
        'Cargo_efetivo',
        'Matricula_siape',
        'Motivo'
    ]


def test_exoneracao_rule(act_exoneracao):
    assert act_exoneracao._rule_for_inst() == r"(EXONERAR)((?=.*Comissao|.*\n.*Comissao|.*Especial|.*\n.*Especial )" + \
        r"[\s\S]*?(?:\.\n|NOMEAR|\d+\-\d+\/\d+\-\d+\.))"


def test_exoneracao_prop_rules_names(act_exoneracao):
    assert list(act_exoneracao._prop_rules()) == [
        "nome",
        "matricula",
        "simbolo",
        "cargo_comissionado",
        "hierarqui_lotacao",
        "orgao",
        "vigencia",
        'Carreira',
        'Fundamento_legal',
        "a_pedido_ou_nao",
        "cargo_efetivo",
        "matricula_SIAPE",
        "motivo",
    ]


def test_exoneracao_prop_rules_rules(act_exoneracao):
    assert list(act_exoneracao._prop_rules().values()) == [
        r"([A-ZÀ-Ž\s]+[A-ZÀ-Ž])",
        r"matricula\s?n?o?\s([\s\S]*?-[\s\S]*?)[,]",
        r"[S|s][í|i]mbolo\s?n?o?\s([\s\S]*?)[,|\s]",
        r"(?:Cargo|Carreira)\sde([\s\S]*?)\,",
        r"(?:[S|s][í|i]mbolo\s?n?o?\s(?:[\s\S]*?)[,|\s])\sde(?:[\s\S]*?),\sd[a|e|o]\s([\s\S]*,?),",
        r"(?:[S|s][í|i]mbolo\s?n?o?\s(?:[\s\S]*?)[,|\s])\sde(?:[\s\S]*?),\sd[a|e|o]\s(?:[\s\S]*,?),\sd[a|e|o]\s([\s\S]*?)$",
        r"",
        r'',
        r'',
        r"(a pedido)",
        r"",
        r"[S|s][I|i][A|a][P|p][E|e]\s[N|n]*[o|O]*\s?([\s\S]*?)[,| | .]",
        r""
    ]


def test_act_exoneracao_consistence_rule(act_exoneracao):
    assert len(act_exoneracao._props_names()) - \
        1 == len(act_exoneracao._prop_rules())


def test_act_exo_com_ner():
    act = Exoneracao(file, 'ner')
    assert isinstance(act._load_model(), sklearn_crfsuite.estimator.CRF)

#
#
#
#
#


@pytest.fixture(name='act_exo_efet')
def fixture_act_exo_efet():
    return ExoneracaoEfetivos(file, 'regex')


def test_exo_efet_backend(act_exo_efet):
    assert act_exo_efet._backend == "regex"


def test_exo_efet_name(act_exo_efet):
    assert act_exo_efet._name == "Exoneração Efetivos"
    assert act_exo_efet.name == "Exoneração Efetivos"
    assert act_exo_efet._act_name() == "Exoneração Efetivos"


def test_exo_efet_flags(act_exo_efet):
    assert act_exo_efet._regex_flags() == 0


def test_exo_efet_prop_names(act_exo_efet):
    assert act_exo_efet._props_names() == [
        "tipo",
        'Nome',
        'Matricula',
        'Cargo_efetivo',
        'Classe',
        'Padrao',
        'Carreira',
        'Quadro',
        'Processo_sei',
        'Vigencia',
        'A_pedido_ou_nao',
        'Motivo',
        'Fundamento_legal',
        'Orgao',
        'Simbolo',
        'Hierarquia_lotacao',
        'Cargo_comissionado'
    ]


def test_exo_efet_rule(act_exo_efet):
    assert act_exo_efet._rule_for_inst(
    ) == r"(EXONERAR,\s?)((?:a\spedido,)?\s(?:[A-Z\\n\s]+),\s(?:matr[ií]cula\s(?:[0-9\.,X-])+)\s" + \
        r"(?!.*\n?.*Cargo\sem\s+Comissao,|.*\n?.*Natureza\sEspecial,)[,\sa-zA-Z0-9\\\/-]*)"


def test_exo_efet_prop_rules_names(act_exo_efet):
    assert list(act_exo_efet._prop_rules()) == [
        "nome",
        "matricula",
        "cargo_efetivo",
        "classe",
        "padrao",
        "carreira",
        "quadro",
        "processo_SEI",
        "data",
        "pedido",
        "motivo",
        "fundamento_legal",
        'Orgao',
        'Simbolo',
        'Hierarquia_lotacao',
        'Cargo_comissionado',
    ]


def test_exo_efet_prop_rules_rules(act_exo_efet):
    assert list(act_exo_efet._prop_rules().values()) == [
        r"^(?:a\spedido,)?\s([A-Z\\n\s]+)",
        r"matr[í|i]cula\s?n?o?\s([\s\S]*?)[,|\s]",
        r"matr[í|i]cula\s?n?o?\s[0-9]+,?([\sa-zA-Z]+)",
        r"matr[í|i]cula\s?n?o?\s[0-9]+,?[\sa-zA-Z]+[,\\n\s]+[eE]specialidade\s?([\sa-zA-Z]+)a\s?contar",
        r"",
        r"",
        r"",
        r"SEI[a-z\s]*([0-9\-\/\n]+)",
        r"a\scontar\sde\s([\s0-9\/]*)",
        r"(a\spedido,)?\s(?:[A-Z\\n\s]+)",
        r"",
        r"nos\stermos\sdo[\n]?([a-zA-Z\s0-9\/]*)",
        r'',
        r'',
        r'',
        r''
    ]


def test_act_exo_efet_consistence_rule(act_exo_efet):
    assert len(act_exo_efet._props_names()) - \
        1 == len(act_exo_efet._prop_rules())


def test_act_exo_efet_ner():
    act = ExoneracaoEfetivos(file, 'ner')
    assert isinstance(act._load_model(), sklearn_crfsuite.estimator.CRF)


#
#
#
#
#

@pytest.fixture(name='act_subs')
def fixture_act_subs():
    return Substituicao(file, 'regex')


def test_substituicao_backend(act_subs):
    assert act_subs._backend == "regex"


def test_substituicao_name(act_subs):
    assert act_subs._name == "Substituição de Funções"
    assert act_subs.name == "Substituição de Funções"
    assert act_subs._act_name() == "Substituição de Funções"


def test_substituicao_flags(act_subs):
    assert act_subs._regex_flags() == re.IGNORECASE


def test_substituicao_prop_names(act_subs):
    assert act_subs._props_names() == [
        "Tipo do Ato",
        'Nome_substituto',
        'Cargo_substituto',
        'Matricula_substituto',
        'Nome_substituido',
        'Matricula_substituido',
        'Simbolo_substituto',
        'Cargo_objeto_substituicao',
        'Simbolo_objeto_substituicao',
        'Hierarquia_lotacao',
        'Orgao',
        'Data_inicial',
        'Data_final',
        'Matricula_siape',
        'Motivo',
    ]


def test_substituicao_rule(act_subs):
    assert act_subs._rule_for_inst() == r"(DESIGNAR)([\s\S]*?)\.\s"


def test_substituicao_prop_rules_names(act_subs):
    assert list(act_subs._prop_rules()) == [
        "nome_substituto",
        "matricula_substituto",
        "nome_substituido",
        "matricula_substituido",
        "cargo_substituto",
        "simbolo_substituto",
        "cargo_objeto_substituicao",
        "simbolo_objeto_substituicao",
        "hierarquia_lotacao",
        "orgao",
        "data_inicial",
        "data_final",
        "matricula_SIAPE",
        "motivo"
    ]


def test_substituicao_prop_rules_rules(act_subs):
    assert list(act_subs._prop_rules().values()) == [
        r"(^[A-ZÀ-Ž\s]+[A-ZÀ-Ž])",
        r"(?:^[A-ZÀ-Ž\s]+[A-ZÀ-Ž])\s[\s\S]*?\smatr[í|i]cula\s?n?o?\s([\s\S]*?)[,|\s]",
        r"para\ssubstituir\s([A-ZÀ-Ž\s]+[A-ZÀ-Ž])",
        r"matr[í|i]cula\s?n?o?\s(?:[\s\S]*?)[\s\S]*?matr[í|i]cula\s?n?o?\s([\s\S]*?),",
        r"para\ssubstituir\s(?:[A-ZÀ-Ž\s]+[A-ZÀ-Ž]),\smatr[í|i]cula\s?n?o?\s(?:[\s\S]*?),\s([\s\S]*?),",
        r"[S|s][í|i]mbolo\s?n?o?\s([\s\S]*?)[,|\s]",
        "",
        r"[S|s][í|i]mbolo\s?n?o?\s(?:[\s\S]*?)[\s\S]*?[S|s][í|i]mbolo\s?n?o?\s([\s\S]*?)",
        "",
        r"(?:[S|s][í|i]mbolo\s?n?o?\s(?:[\s\S]*?)[,|\s])\sde(?:[\s\S]*?),\sd[a|e|o]\s(?:[\s\S]*,?),\sd[a|e|o]\s([\s\S]*?)$",
        "",
        "",
        r"[S|s][I|i][A|a][P|p][E|e]\s[N|n]?[o|O]?\s([\s\S]*?)[,| | .]",
        ""
    ]


def test_act_substitution_consistence_rule(act_subs):
    assert len(act_subs._props_names())-1 == len(act_subs._prop_rules())


def test_act_substituicao_ner():
    act = Substituicao(file, 'ner')
    assert isinstance(act._load_model(), sklearn_crfsuite.estimator.CRF)

#
#
#
#
#


@pytest.fixture(name='act_revert')
def fixture_act_revert():
    return Revertions(file, 'regex')


def test_revertions_backend(act_revert):
    assert act_revert._backend == "regex"


def test_revertions_name(act_revert):
    assert act_revert._name == "Reversão"
    assert act_revert.name == "Reversão"
    assert act_revert._act_name() == "Reversão"


def test_revertions_flags(act_revert):
    assert act_revert._regex_flags() == re.IGNORECASE


def test_revertions_prop_names(act_revert):
    assert act_revert._props_names() == [
        "Tipo do Ato",
        'Processo_sei',
        'Nome',
        'Matricula',
        'Cargo_efetivo',
        'Classe',
        'Padrao',
        'Quadro',
        'Fundamento_legal',
        'Orgao',
        'Vigencia',
    ]


def test_revertions_rule(act_revert):
    assert act_revert._rule_for_inst(
    ) == r"(reverter\sa\satividade[,|\s])([\s\S]*?(?<!lei)\s(?:[0-9|\s]*?[.|-]\s?)+?[0-9|\s]*/\s?[0-9|\s]*-?\s?[0-9|\s]*[.|,])"


def test_revertions_prop_rules_names(act_revert):
    assert list(act_revert._prop_rules()) == [
        "processo_SEI",
        "nome",
        "matricula",
        "cargo_efetivo",
        "classe",
        "padrao",
        "quadro",
        "fundamento_legal",
        "orgao",
        "vigencia",
        # "matriucla_SIAPE"
    ]


def test_revertions_prop_rules_rules(act_revert):
    assert list(act_revert._prop_rules().values()) == [
        r"(?<!lei)\s((?:[0-9|\s]*?[.|-]\s?)+?[0-9|\s]*/\s?[0-9|\s]*-?\s?[0-9|\s]*)[.|,]",
        r"\s([^,]*?),\smatricula",
        r"matricula\s?n?o?\s([\s\S]*?-[\s\S]*?)[,]",
        r"(?:Cargo|Carreira)\sde([\s\S]*?)\,",
        r"(?:([^,]*?)\sclasse,)?(?(1)|classe\s([\s\S]*?),)",
        r"[p|P]adr[a|ã]o\s([\s\S]*?),",
        r"d?[e|a|o]?(Quadro[\s\S]*?)[,|;|.]",
        r"nos\stermos\sdo\s([\s\S]*?),\sa?\s",
        r"Lotacao:|Quadro\sde\sPessoal\sd[a|e|o]([\s\S]*?)[.|,]",
        "",
        # r"siape\sn?o?\s([\s\S]*?)[,| | .]"
    ]


def test_act_revertions_consistence_rule(act_revert):
    assert len(act_revert._props_names())-1 == len(act_revert._prop_rules())


def test_act_revertions_ner():
    act = Revertions(file, 'ner')
    assert isinstance(act._load_model(), sklearn_crfsuite.estimator.CRF)

#
#
#
#
#


@pytest.fixture(name='act_nomcom')
def fixture_act_nomcom():
    return NomeacaoComissionados(file, 'regex')


def test_nom_com_backend(act_nomcom):
    assert act_nomcom._backend == "regex"


def test_nom_com_name(act_nomcom):
    assert act_nomcom._name == "Nomeação"
    assert act_nomcom.name == "Nomeação"
    assert act_nomcom._act_name() == "Nomeação"


def test_nom_com_flags(act_nomcom):
    assert act_nomcom._regex_flags() == 0


def test_nom_com_prop_names(act_nomcom):
    assert act_nomcom._props_names() == [
        'Tipo do Ato',
        'Nome',
        'Cargo_efetivo',
        'Matricula',
        'Matricula_siape',
        'Simbolo',
        'Cargo_comissionado',
        'Hierarquia_lotacao',
        'Orgao',
        'Cargo',
        'Numero_dodf_resultado_final',
        'Fundamento_legal',
        'Carreira',
    ]


def test_nom_com_rule(act_nomcom):
    assert act_nomcom._rule_for_inst(
    ) == r"(NOMEAR)([\s\S]*?)((\.\s)|(?=(EXONERAR|NOMEAR)))"


def test_nom_com_prop_rules_names(act_nomcom):
    assert list(act_nomcom._prop_rules()) == [
        "nome",
        "cargo_efetivo",
        "matricula",
        "matricula_SIAPE",
        "simbolo",
        "cargo_comissionado",
        "hierarquia_lotacao",
        "orgao",
        'Cargo',
        'Numero_dodf_resultado_final',
        'Fundamento_legal',
        'Carreira',
    ]


def test_nom_com_prop_rules_rules(act_nomcom):
    assert list(act_nomcom._prop_rules().values()) == [
        r"(^[A-ZÀ-Ž\s]+[A-ZÀ-Ž])",
        r"(?:^[A-ZÀ-Ž\s]+[A-ZÀ-Ž]),\s(?![M|m]atr[i|í]cula)([\s\S]*?),\s",
        r"[M|m]atr[í|i]cula\s?n?o?\s([\s\S]*?)[,|\s]",
        r"[S|s][I|i][A|a][P|p][E|e]\s[N|n]?[o|O]?\s([\s\S]*?)[,| | .]",
        r"[S|s][í|i]mbolo\s?n?o?\s([\s\S]*?)[,|\s]",
        r"(?:[S|s][í|i]mbolo\s?n?o?\s(?:[\s\S]*?)[,|\s])\sde([\s\S]*?),",
        r"(?:[S|s][í|i]mbolo\s?n?o?\s(?:[\s\S]*?)[,|\s])\sde(?:[\s\S]*?),\sd[a|e|o]\s([\s\S]*,?),",
        r"(?:[S|s][í|i]mbolo\s?n?o?\s(?:[\s\S]*?)[,|\s])\sde(?:[\s\S]*?),\sd[a|e|o]\s(?:[\s\S]*,?),\sd[a|e|o]\s([\s\S]*?)$",
        r'',
        r'',
        r'',
        r'',
    ]


def test_act_nom_com_consistence_rule(act_nomcom):
    assert len(act_nomcom._props_names())-1 == len(act_nomcom._prop_rules())


def test_act_nom_com_ner():
    act = NomeacaoComissionados(file, 'ner')
    assert isinstance(act._load_model(), sklearn_crfsuite.estimator.CRF)

#
#
#
#
#


@pytest.fixture(name='act_nom_efet')
def fixture_act_nom_efet():
    return NomeacaoEfetivos(file, 'regex')


def test_nom_efet_backend(act_nom_efet):
    assert act_nom_efet._backend == "regex"


def test_nom_efet_name(act_nom_efet):
    assert act_nom_efet._name == "Nomeação de Efetivos"
    assert act_nom_efet.name == "Nomeação de Efetivos"
    assert act_nom_efet._act_name() == "Nomeação de Efetivos"


def test_nom_efet_flags(act_nom_efet):
    assert act_nom_efet._regex_flags() == 0


def test_nom_efet_prop_names(act_nom_efet):
    assert act_nom_efet._props_names() == [
        'tipo',
        'Edital_normativo',
        'Data_edital_normativo',
        'Numero_dodf_edital_normativo',
        'Data_dodf_edital_normativo',
        'Edital_resultado_final',
        'Data_edital_resultado_final',
        'Numero_dodf_resultado_final',
        'Data_dodf_resultado_final',
        'Cargo',
        'Especialidade',
        'Carreira',
        'Orgao',
        'Candidato',
        'Classe',
        'Quadro',
        'Candidato_pne',
        'Padrao',
    ]


def test_nom_efet_rule(act_nom_efet):
    assert act_nom_efet._rule_for_inst(
    ) == r"(NOMEAR\s)((?:[ao]s\scandidat[ao]s\sabaixo(?:([a-zA-Z_0-9,\s\/-\:\-\(\);](no?\.)?)*).|" + \
        r"(?:[ao]\scandidat[oa]\sabaixo(?:([a-zA-Z_0-9,\s\/-\:\-\(\);](no?\.)?)*)))(?:\s[a-zA-Z_\s]*(?:deficiencia|especiais):(?:\s[\sA-Zo]+" + \
        r",\s?\d{1,4}o?;?)+)?(?:\s)?(?:[\r\n\t\f\sa-zA-Z_\s]*classificacao:(?:\s[\sA-Zo]+,\s?\d{1,4}o?[,;]?)+)?)"


def test_nom_efet_prop_rules_names(act_nom_efet):
    assert list(act_nom_efet._prop_rules()) == [
        "edital_normativo",
        "data_edital_normativo",
        "numero_dodf_edital_normativo",
        "data_dodf_edital_normativo",
        "edital_resultado_final",
        "data_edital_resultado_final",
        'Numero_dodf_resultado_final',
        'Data_dodf_resultado_final',
        "cargo",
        "especialiade",
        "carreira",
        "orgao",
        "candidato",
        "classificacao",
        "pne",
        "processo_SEI",
        'Padrao',
    ]


def test_nom_efet_prop_rules_rules(act_nom_efet):
    assert list(act_nom_efet._prop_rules().values()) == [
        r"Edital\s(?:[Nn]ormativo|de\s[Aa]bertura)\sno\s([\/\s\-a-zA-Z0-9_]+)",
        r"",
        r"publicado\sno\sDODF\sno\s(\d{1,3})",
        r"publicado\sno\sDODF\sno\s\d{1,3},\s?de([\s0-9a-or-vzç]*\d{4})",
        r"Resultado\sFinal\sno\s([\/\s\-a-zA-Z0-9_]+)",
        r"",
        r'',
        r'',
        r"DODF\sno\s\d{1,3}(?:,[\s0-9a-or-vzç]*\d{4}),[\sa-z]*([A-Z\s]+)",
        r"[\s,a-z\(\:\)]+([\sA-Z\-]*):",
        r"[cC]arreira\s(?:d[ae]\s)?([a-zA-Z\s]+)",
        r"[cC]arreira\s(?:d[ae]\s)?(?:[a-zA-Z\s]+),\s?d?[ao]?\s?([\sa-zA-Z0-9_]*)",
        r"(?:[\sA-Z\-]*):(?:[\sa-zC]*:)?\s([\sA-Z0-9\,o\;]+)",
        r"",
        r"(?:deficiencia|especiais):\s([\sA-Z0-9\,o\;]+)",
        r"(?<!lei)\s((?:[0-9|\s]*?[.|-]\s?)+?[0-9|\s]*/\s?[0-9|\s]*-?\s?[0-9|\s]*)[.|,]",
        r''
    ]


def test_act_nom_efet_consistence_rule(act_nom_efet):

    assert len(act_nom_efet._props_names()) - \
        1 == len(act_nom_efet._prop_rules())


def test_act_nom_efet_ner():
    act = NomeacaoEfetivos(file, 'ner')
    assert isinstance(act._load_model(), sklearn_crfsuite.estimator.CRF)

#
#
#
#


def test_act_cessao_ner():
    act = Cessoes(file, 'ner')
    assert isinstance(act._load_model(), sklearn_crfsuite.estimator.CRF)


def test_act_sem_efeito_apo_ner():
    act = SemEfeitoAposentadoria(file, 'ner')
    assert isinstance(act._load_model(), sklearn_crfsuite.estimator.CRF)
