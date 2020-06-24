====
Acts
====

Acts are build always as a child class from the Base class :obj:`Atos`. Following are the base class structure
and a guide for implementating your own act. Also, a list of implementated and missing acts are presented.

Base Class
==========

.. autoclass:: dodfminer.extract.regex.atos.base.Atos
    :members:

Implementing new acts
=====================

The Acts base class is build in a way to make easy implementation of new acts.
A programmer seeking to help with regex rules, need not to worry about anything, besides
the regex itself. 

Mainly, the following four funcions need to be overwrited in the child class.

.. automethod:: dodfminer.extract.regex.atos.base.Atos._act_name

.. automethod:: dodfminer.extract.regex.atos.base.Atos._props_names

.. automethod:: dodfminer.extract.regex.atos.base.Atos._inst_rule

.. automethod:: dodfminer.extract.regex.atos.base.Atos._prop_rules

Additionaly, if the programmer whishes to change the regex flags
for his/her class, they can overwrite the following function in the child
class:

.. automethod:: dodfminer.extract.regex.atos.base.Atos._regex_flags

Change the Core File
--------------------

After all functions have been implemented, the programmer needs to do a minor change in the core file.
The following must be added::

    from dodfminer.extract.regex.atos.act_file_name import NewActClass
    _acts_ids["new_act_name"] = NewActClass

Base Class Mechanisms
=====================

One does not access directly none of those functions, but they are listed here in case the programmer
implementing the act needs more informations.

.. automethod:: dodfminer.extract.regex.atos.base.Atos._find_instances

.. automethod:: dodfminer.extract.regex.atos.base.Atos._extract_instances

.. automethod:: dodfminer.extract.regex.atos.base.Atos._find_props

.. automethod:: dodfminer.extract.regex.atos.base.Atos._act_props

.. automethod:: dodfminer.extract.regex.atos.base.Atos._acts_props

.. automethod:: dodfminer.extract.regex.atos.base.Atos._build_dataframe

Implemented Acts
================

- Abono
- Aposentadoria
- Exoneração
- Nomeação
- Retificações
- Reversões
- Substituições

Missing Acts
============

- Cessões
- Tornar sem efeito Aposentadoria
- Exoneração de Cargos Efetivos
