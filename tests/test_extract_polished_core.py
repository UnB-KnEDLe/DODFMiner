import os

from dodfminer.extract.polished.core import ActsExtractor, _acts_ids

from dodfminer.extract.polished.acts.aposentadoria import Retirements, RetAposentadoria
from dodfminer.extract.polished.acts.cessoes import Cessoes
from dodfminer.extract.polished.acts.nomeacao import NomeacaoComissionados, NomeacaoEfetivos
from dodfminer.extract.polished.acts.exoneracao import Exoneracao, ExoneracaoEfetivos
from dodfminer.extract.polished.acts.reversoes import Revertions
from dodfminer.extract.polished.acts.abono import AbonoPermanencia
from dodfminer.extract.polished.acts.sem_efeito_aposentadoria import SemEfeitoAposentadoria
from dodfminer.extract.polished.acts.substituicao import Substituicao
from dodfminer.extract.polished.acts.contrato import Contratos


from dodfminer.extract.polished.create_xml import XMLFy


def test_polished_core_acts():
    assert _acts_ids == {
        "aposentadoria": Retirements,
        "reversoes": Revertions,
        "nomeacao": NomeacaoComissionados,
        "exoneracao": Exoneracao,
        "abono": AbonoPermanencia,
        "retificacoes": RetAposentadoria,
        "substituicao": Substituicao,
        "efetivos_nome": NomeacaoEfetivos,
        "efetivos_exo": ExoneracaoEfetivos,
        "sem_efeito_aposentadoria": SemEfeitoAposentadoria,
        "cessoes": Cessoes,
        "contrato": Contratos
    }


def test_polished_core_act_obj():
    assert isinstance(ActsExtractor.get_act_obj(
        "aposentadoria", "", "regex"), Retirements)
    assert isinstance(ActsExtractor.get_act_obj(
        "reversoes", "", "regex"), Revertions)
    assert isinstance(ActsExtractor.get_act_obj(
        "nomeacao", "", "regex"), NomeacaoComissionados)
    assert isinstance(ActsExtractor.get_act_obj(
        "abono", "", "regex"), AbonoPermanencia)
    assert isinstance(ActsExtractor.get_act_obj(
        "retificacoes", "", "regex"), RetAposentadoria)
    assert isinstance(ActsExtractor.get_act_obj(
        "substituicao", "", "regex"), Substituicao)
    assert isinstance(ActsExtractor.get_act_obj(
        "efetivos_nome", "", "regex"), NomeacaoEfetivos)
    assert isinstance(ActsExtractor.get_act_obj(
        "efetivos_exo", "", "regex"), ExoneracaoEfetivos)
    assert isinstance(ActsExtractor.get_act_obj(
        "exoneracao", "", "regex"), Exoneracao)
    assert isinstance(ActsExtractor.get_act_obj(
        "sem_efeito_aposentadoria", "", "regex"), SemEfeitoAposentadoria)
    assert isinstance(ActsExtractor.get_act_obj(
        "cessoes", "", "regex"), Cessoes)
    assert isinstance(ActsExtractor.get_act_obj(
        "contrato", "", "regex"), Contratos)
    assert len(_acts_ids) == 12


def test_polished_core_get_all_obj():
    objs = ActsExtractor.get_all_obj("", "regex")
    needed = {
        "abono": AbonoPermanencia("", "regex"),
        "aposentadoria": Retirements("", "regex"),
        "efetivos_exo": ExoneracaoEfetivos("", "regex"),
        "efetivos_nome": NomeacaoEfetivos("", "regex"),
        "exoneracao": Exoneracao("", "regex"),
        "nomeacao": NomeacaoComissionados("", "regex"),
        "retificacoes": RetAposentadoria("", "regex"),
        "reversoes": Revertions("", "regex"),
        "substituicao": Substituicao("", "regex"),
        "sem_efeito_aposentadoria": SemEfeitoAposentadoria("", "regex"),
        "cessoes": Cessoes("", "regex"),
        "contrato": Contratos("", "regex")
    }
    assert len(objs) == 12
    assert len(objs) == len(needed)


def test_polished_core_get_all_obj_parallel():
    objs = ActsExtractor.get_all_obj_parallel("", "regex")
    needed = {
        "abono": AbonoPermanencia("", "regex"),
        "aposentadoria": Retirements("", "regex"),
        "efetivos_exo": ExoneracaoEfetivos("", "regex"),
        "efetivos_nome": NomeacaoEfetivos("", "regex"),
        "exoneracao": Exoneracao("", "regex"),
        "nomeacao": NomeacaoComissionados("", "regex"),
        "retificacoes": RetAposentadoria("", "regex"),
        "reversoes": Revertions("", "regex"),
        "substituicao": Substituicao("", "regex"),
        "sem_efeito_aposentadoria": SemEfeitoAposentadoria("", "regex"),
        "cessoes": Cessoes("", "regex"),
        "contrato": Contratos("", "regex")
    }
    assert len(objs) == 12
    assert len(objs) == len(needed)


def test_polished_core_act_df():
    assert isinstance(ActsExtractor.get_act_df("aposentadoria", "", "regex"), type(Retirements("", "regex").data_frame))
    assert isinstance(ActsExtractor.get_act_df("reversoes", "", "regex"), type(Revertions("", "regex").data_frame))
    assert isinstance(ActsExtractor.get_act_df("nomeacao", "", "regex"), type(NomeacaoComissionados("", "regex").data_frame))
    assert isinstance(ActsExtractor.get_act_df("abono", "", "regex"), type(AbonoPermanencia("", "regex").data_frame))
    assert isinstance(ActsExtractor.get_act_df("retificacoes", "", "regex"), type(RetAposentadoria("", "regex").data_frame))
    assert isinstance(ActsExtractor.get_act_df("substituicao", "", "regex"), type(Substituicao("", "regex").data_frame))
    assert isinstance(ActsExtractor.get_act_df("efetivos_nome", "", "regex"), type(NomeacaoEfetivos("", "regex").data_frame))
    assert isinstance(ActsExtractor.get_act_df("efetivos_exo", "", "regex"), type(ExoneracaoEfetivos("", "regex").data_frame))
    assert isinstance(ActsExtractor.get_act_df("exoneracao", "", "regex"), type(Exoneracao("", "regex").data_frame))
    assert isinstance(ActsExtractor.get_act_df("sem_efeito_aposentadoria", "", "regex"), type(SemEfeitoAposentadoria("", "regex").data_frame))
    assert isinstance(ActsExtractor.get_act_df("cessoes", "", "regex"), type(Cessoes("", "regex").data_frame))
    assert isinstance(ActsExtractor.get_act_df("contrato", "", "regex"), type(Contratos("", "regex").data_frame))
    assert len(_acts_ids) == 12


def test_polished_core_get_all_df():
    data_frames = ActsExtractor.get_all_df("", "regex")
    dataframes = {
        "abono": AbonoPermanencia("", "regex").data_frame,
        "aposentadoria": Retirements("", "regex").data_frame,
        "efetivos_exo": ExoneracaoEfetivos("", "regex").data_frame,
        "efetivos_nome": NomeacaoEfetivos("", "regex").data_frame,
        "exoneracao": Exoneracao("", "regex").data_frame,
        "nomeacao": NomeacaoComissionados("", "regex").data_frame,
        "retificacoes": RetAposentadoria("", "regex").data_frame,
        "reversoes": Revertions("", "regex").data_frame,
        "substituicao": Substituicao("", "regex").data_frame,
        "sem_efeito_aposentadoria": SemEfeitoAposentadoria("", "regex").data_frame,
        "cessoes": Cessoes("", "regex").data_frame,
        "contrato": Contratos("", "regex").data_frame
    }
    assert len(data_frames) == 12
    assert len(data_frames) == len(dataframes)


def test_polished_core_get_all_df_parallel():
    data_frames = ActsExtractor.get_all_df_parallel("", "regex")
    dataframes = {
        "abono": AbonoPermanencia("", "regex").data_frame,
        "aposentadoria": Retirements("", "regex").data_frame,
        "efetivos_exo": ExoneracaoEfetivos("", "regex").data_frame,
        "efetivos_nome": NomeacaoEfetivos("", "regex").data_frame,
        "exoneracao": Exoneracao("", "regex").data_frame,
        "nomeacao": NomeacaoComissionados("", "regex").data_frame,
        "retificacoes": RetAposentadoria("", "regex").data_frame,
        "reversoes": Revertions("", "regex").data_frame,
        "substituicao": Substituicao("", "regex").data_frame,
        "sem_efeito_aposentadoria": SemEfeitoAposentadoria("", "regex").data_frame,
        "cessoes": Cessoes("", "regex").data_frame,
        "contrato": Contratos("", "regex").data_frame
    }
    assert len(data_frames) == 12
    assert len(data_frames) == len(dataframes)


def test_polished_get_xml():
    xml = ActsExtractor.get_xml(""+os.path.dirname(__file__) +
                                "/support/DODF 001 01-01-2019 EDICAO ESPECIAL.pdf", "regex", 0)
    assert isinstance(xml, XMLFy)
