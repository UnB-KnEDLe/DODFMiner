====
Acts
====

.. contents:: Table of Contents

Acts are always built as a child class from the Base class :obj:`Atos`. Following are the base class structure
and a guide for implementating your own act. Also, a list of implementated and missing acts are presented.

Base Class
==========

.. autoclass:: dodfminer.extract.polished.acts.base.Atos
    :members:

Implementing new acts
=====================

The Acts base class is build in a way to make easy implementation of new acts.
A programmer seeking to help in the development of new acts, need not to worry about anything, besides
the regex or ner itself.

Mainly, the following funcions need to be overwrited in the child class.

.. automethod:: dodfminer.extract.polished.acts.base.Atos._act_name

.. automethod:: dodfminer.extract.polished.acts.base.Atos._props_names

Regex Methods
^^^^^^^^^^^^^

In case you want to extract through regex, the following funcions needs to be written:

.. automethod:: dodfminer.extract.polished.backend.regex.ActRegex._rule_for_inst
    :noindex:

.. automethod:: dodfminer.extract.polished.backend.regex.ActRegex._prop_rules
    :noindex:

Additionaly, if the programmer whishes to change the regex flags
for his/her class, they can overwrite the following function in the child
class:

.. automethod:: dodfminer.extract.polished.backend.regex.ActRegex._regex_flags
    :noindex:

NER Methods
^^^^^^^^^^^

If NER will be used, you shall add a trained model to the acts/models folder. Also the following method should be overwrited in your act:

.. automethod:: dodfminer.extract.polished.backend.ner.ActNER._load_model
    :noindex:

Change the Core File
^^^^^^^^^^^^^^^^^^^^

After all functions have been implemented, the programmer needs to do a minor change in the core file.
The following must be added::

    from dodfminer.extract.polished.acts.act_file_name import NewActClass
    _acts_ids["new_act_name"] = NewActClass

Base Class Mechanisms
=====================

One does not access directly none of those functions, but they are listed here in case the programmer
implementing the act needs more informations.

.. automethod:: dodfminer.extract.polished.acts.base.Atos._extract_instances

.. automethod:: dodfminer.extract.polished.acts.base.Atos._extract_props

.. automethod:: dodfminer.extract.polished.acts.base.Atos._build_dataframe

Implemented Acts and Properties
================

- Abono
    * Nome
    * Matricula
    * Cargo_efetivo
    * Classe
    * Padrao
    * Quadro
    * Fundamento_legal
    * Orgao
    * Processo_sei
    * Vigencia
    * Matricula_siape
    * Cargo
    * Lotacao

- Aposentadoria
    * Ato
    * Processo
    * Nome_ato
    * Cod_matricula_ato
    * Cargo
    * Classe
    * Padrao
    * Quadro
    * Fund_legal
    * Empresa_ato

- Exoneração Efetivos
    * Nome
    * Matricula
    * Cargo_efetivo
    * Classe
    * Padrao
    * Carreira
    * Quadro
    * Processo_sei
    * Vigencia
    * A_pedido_ou_nao
    * Motivo
    * Fundamento_legal
    * Orgao
    * Simbolo
    * Hierarquia_lotacao
    * Cargo_comissionado

- Exoneração Comissionados
    * Nome
    * Matricula
    * Simbolo
    * Cargo_comissionado
    * Hierarquia_lotacao
    * Orgao
    * Vigencia
    * Carreir
    * Fundamento_legal
    * A_pedido_ou_nao
    * Cargo_efetivo
    * Matricula_siape
    * Motivo

- Nomeação Efetivos
    * Edital_normativo
    * Data_edital_normativo
    * Numero_dodf_edital_normativo
    * Data_dodf_edital_normativo
    * Edital_resultado_final
    * Data_edital_resultado_final
    * Numero_dodf_resultado_final
    * Data_dodf_resultado_final
    * Cargo
    * Especialidade
    * Carreira
    * Orgao
    * Candidato
    * Classe
    * Quadro
    * Candidato_pne
    * Padrao

- Nomeação Comissionados
    * Edital_normativo
    * Data_edital_normativo
    * Numero_dodf_edital_normativo
    * Data_dodf_edital_normativo
    * Edital_resultado_final
    * Data_edital_resultado_final
    * Numero_dodf_resultado_final
    * Data_dodf_resultado_final
    * Cargo
    * Especialidade
    * Carreira
    * Orgao
    * Candidato
    * Classe
    * Quadro
    * Candidato_pne
    * Padrao

- Retificações de Aposentadoria
    * Tipo do Ato,
    * Tipo de Documento
    * Número do documento
    * Data do documento 
    * Número do DODF
    * Data do DODF
    * Página do DODF
    * Nome do Servidor
    * Matrícula
    * Cargo
    * Classe
    * Padrao
    * Matricula SIAPE
    * Informação Errada
    * Informação Corrigida


- Reversões
    * Processo_sei
    * Nome
    * Matricula
    * Cargo_efetivo
    * Classe
    * Padrao
    * Quadro
    * Fundamento_legal
    * Orgao
    * Vigencia

- Substituições
    * Nome_substituto
    * Cargo_substituto
    * Matricula_substituto
    * Nome_substituido
    * Matricula_substituido
    * Simbolo_substitut
    * Cargo_objeto_substituicao
    * Simbolo_objeto_substituicao
    * Hierarquia_lotacao
    * Orgao
    * Data_inicial
    * Data_final
    * Matricula_siape
    * Motivo

- Cessões
    * nome
    * matricula
    * cargo_efetivo
    * classe
    * padrao
    * orgao_cedente
    * orgao_cessionario
    * onus
    * fundamento legal
    * processo_SEI
    * vigencia
    * matricula_SIAPE
    * cargo_orgao_cessionario
    * simbolo
    * hierarquia_lotaca

- Tornar sem efeito Aposentadoria
    * tipo_documento
    * numero_documento
    * data_documento
    * numero_dodf
    * data_dodf
    * pagina_dodf
    * nome
    * matricula
    * matricula_SIAPE
    * cargo_efetivo
    * classe
    * padrao
    * quadro
    * orgao
    * processo_SE



