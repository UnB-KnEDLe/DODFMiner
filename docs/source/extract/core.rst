==============
Extractor Core
==============

.. contents:: Table of Contents

.. automodule:: dodfminer.extract.core

Extract Class
=============

.. autoclass:: dodfminer.extract.core.ContentExtractor
    :members:

Downloader Private Members
==========================

One does not access directly none of those methods, but they are listed here in case the programmer
using the extract library needs more informations.

Text Preprocessing
------------------

.. automethod:: dodfminer.extract.core.ContentExtractor._normalize_text

.. automethod:: dodfminer.extract.core.ContentExtractor._extract_titles


Check Existence
---------------

.. automethod:: dodfminer.extract.core.ContentExtractor._get_pdfs_list

.. automethod:: dodfminer.extract.core.ContentExtractor._get_json_list

.. automethod:: dodfminer.extract.core.ContentExtractor._get_txt_list


Directory Handling
------------------

.. automethod:: dodfminer.extract.core.ContentExtractor._struct_subfolders

.. automethod:: dodfminer.extract.core.ContentExtractor._create_single_folder


Others
------

.. automethod:: dodfminer.extract.core.ContentExtractor._log