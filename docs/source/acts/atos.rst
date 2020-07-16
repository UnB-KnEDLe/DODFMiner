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

Implemented Acts
================

- Abono
- Aposentadoria
- Exoneração
- Nomeação
- Retificações
- Reversões
- Substituições
- Cessões
- Tornar sem efeito Aposentadoria
- Exoneração de Cargos Efetivos



