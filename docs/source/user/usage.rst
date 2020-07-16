===============
Using DODFMiner
===============

.. contents:: Table of Contents

Command-Line Usage
==================

Considering the module has been installed using pip, you should be able to use DODFMiner as a command line program. To check if installation has been done successfully run::

    $ dodfminer --help

A help screen of the program should appear. The helper sould show two positional arguments: *downloader* and *extract*.
Each of those arguments can be considered as a subprogram and work independently, you can choose the one you desire using::

    $ dodfminer downloader --help
    $ dodfminer extract --help

Depending which module you choose the execution parameters will change.

Downloader Module
-----------------

The downloader module is responsible for downloading DODF PDFs from the website.
It allows you to choose the start and end date of the files you want to download.
Also, you can choose where to save them.
Following are the list of avaiable parameters, their description and the default value.

.. note::
    This module relies on internet connection and can fail if internet is not working properly.
    Also, the execution might take a while if there are a huge ammount of pdfs to download.

Parameters Table
^^^^^^^^^^^^^^^^

+------------------+-----------------------------------------+---------+
| Argument         | Description                             | Default |
+==================+=========================================+=========+
| -sp --save_path  | Folder to output the download DODFs     | ./      |
+------------------+-----------------------------------------+---------+
| -sd --start_date | Input the date in either mm/yy or mm-yy | 01/19   |
+------------------+-----------------------------------------+---------+
| -ed --end_date   | Input the date in either mm/yy or mm-yy | 01/19   |
+------------------+-----------------------------------------+---------+

Usage Example::

    $ dodfminer downloader -sd 01/03 -ed 12/20

Extractor Module
----------------

The extractor module is responsible for extracting information from DODF PDFs and save it
in a desirable format.

The extraction can be made, to a pure text content, where a DODF will be converted to TXT or JSON. Or,
additionaly, the extraction can be done in a polished way, where from the DODF will be extracted to acts and
its given proprieties in a CSV format.

Pure extraction
^^^^^^^^^^^^^^^

Given a -t flag, it allows you to choose the output format between three options: blocks of text with tiles,
pure text in .txt format and text separated by titles:

- **Blocks of Text**: Outputs a JSON file that extract text blocks.
- **Pure Text**: Output a .txt file, with raw text from the pdf.
- **Blocks of Text with Titles**: Outputs a JSON file that extract text blocks indexed by titles.

Polished Extraction
^^^^^^^^^^^^^^^^^^^

Using the -a or --act flag, you can extract the dodf in a polished way. The usage of the -a will extract all types
of act in the DODF. Additionaly, if desired, the flag can followed by a list of specific acts types which you want to extract.
The extraction is done using the backend specified in the -b flag, which can be either regex or ner.

Available Act Types:

    - aposentadoria
    - reversoes
    - nomeacao
    - exoneracao
    - abono
    - retificacoes
    - substituicao
    - cessoes
    - sem_efeito_aposentadoria
    - efetivos_nome
    - efetivos_exo



Parameters Table
^^^^^^^^^^^^^^^^

Following are the list of avaiable parameters, their description and the default value.

+-------------------------+------------------------------------------+------------+
| Argument                | Description                              | Default    |
+=========================+==========================================+============+
| -i --input_folder       | Path to the PDFs folder                  | ./         |
+-------------------------+------------------------------------------+------------+
| -s --single-file        | Path to a single PDF                     | None       |
+-------------------------+------------------------------------------+------------+
| -t --type-of-extraction | Type of text extraction                  | pure-text  |
+-------------------------+------------------------------------------+------------+
| -a --act                | List of acts that will be extract to CSV | None       |
+-------------------------+------------------------------------------+------------+
| -b --backend            | Which backend will extract the acts      | regex      |
+-------------------------+------------------------------------------+------------+


Usage Example::

    $ dodfminer extract -i path/to/pdf/folder -t with-titles
    $ dodfminer extract -s path/to/dodf.pdf -t pure-text
    $ dodfminer extract -s path/to/dodf.pdf -a nomeacao
    $ dodfminer extract -s path/to/dodf.pdf -a nomeacao cessoes -b ner

.. note::

    It's important to notice that if -t and -a options are used together the -t option will
    have the priority and the -a will not execute.

.. note::

    The DODFMiner act extraction needs the text data from DODFs to correct extract the acts
    from DODF, therefore the -a option generates first txt files before the act extraction.

Library Usage
=============

The DODFMiner was created also thinking the user might want to use it as a library in their own projects.
Users can use install the DODFMiner and call its modules and functions in their python scripts. Following are
some of the imports you might want to do, while using as a library::

    from dodfminer import acts
    from dodfminer import Downloader
    from dodfminer import ActsExtractor
    from dodfminer import ContentExtractor

The details of using the DODFMiner modules and functions are described in this documentation, in the following sections.
