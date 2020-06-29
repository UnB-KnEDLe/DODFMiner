# Architecture's Document

Python is surprisingly flexible when it comes to structuring your applications. On the one hand, this flexibility is great: it allows different use cases to use structures that are necessary for those use cases. On the other hand, though, it can be very confusing to the new developer.

### Document Overview

| Topic                        | Description                                                                                                                                                             |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Introduction                 | Describes information about the purpose of this document.                                                                                                               |
| Architectural Representation | Provides a description of the software architecture for a better understanding of its structure and functioning.<br>In addition to showing how it is being represented. |
| Goals and Constraints        | Provides a description of the requirements and objectives of the software,<br>and whether they have any impact on the architecture.                                     |
| Logical View                 | Provides a description of the relevant parts related to the architecture of the design model.                                                                           |
| References                   | Relevant links and literatures to the development of this document.                                                                                                     |

## Introduction
---------------

### Objetive

This document aims to provide an overview of the architecture of the DODFMiner Library: it contains pertinent information about the architecture model adopted, such as diagrams that illustrate use cases, package diagram, among other resources.

### Escope

Through this document, the reader will be able to understand the functioning of the DODFMiner Library, as well as the approach used in its development. In this way, it will be possible to have a broad understanding of its architecture.

### Definitions, Acronyms and Abreviations

| Acronym       | Definition             |
|---------------|------------------------|
| CLI           | Command Line Interface |


### Revision History

| Data     | Versão | Descrição          | Autor        | 
|----------|--------|--------------------|--------------|
|29/06/2020| 1.0    | Documment Creation | Renato Nobre |


## Architectural Representation
-------------------------------

The main point to understand in this architecture is that the DODFMiner is a library and a CLI application simultaniously. DODFMiner can be integrated to another project or used standalone in a shell environment.

Being a library requires a given ammount of complexity. In larger applications, you may have one or more internal packages that provide specific functionality to a larger library you are packaging. This application follows this aspect, mining pdf documents, imply in many subpackages with specific functionality, that when working together, fulfill a greater aspect.

### Relationship Diagram 

### Subpackages Representations

#### Main Application

#### Downloader

#### Extractor

### Patterns

### Technologies

1. **MuPDF**

   MuPDF is a free and open-source software framework written in C that implements a PDF, XPS, and EPUB parsing and rendering engine. It is used primarily to render pages into bitmaps, but also provides support for other operations such as searching and listing the table of contents and hyperlinks

2. **BeautifulSoup**

   Beautiful Soup is a Python package for parsing HTML and XML documents. It creates a parse tree for parsed pages that can be used to extract data from HTML, which is useful for web scraping

3. **Pandas**

    Pandas is a software library written for the Python programming language for data manipulation and analysis. In particular, it offers data structures and operations for manipulating numerical tables and time series. It is free software released under the three-clause BSD license

4. Site do DODF 


## Goals and Constraints
------------------------

### Non-functional Requirements

* Be a library avaiable by pip on [The Python Package Index (PyPI)](https://pypi.org)
* Work as a standalone command line application, installed globally without needing file execution
* Support continuous deployment and continuous integration
* The DODFMiner should be able to:
    - Download DODFs from the website
    - Extract pdf files to .txt and .json formats
    - Extract images and tables from the DODF
    - Extract DODF's Acts and its proprieties to a dataframe or other desirable format

### General Constraints

* Have tested support for Mac and Linux users.
* Have a docker installation method
* Be open-source
* Don't use a database library

### Tecnological Constraints

* Python: Language used for development
* MuPDF: Tool used for PDF extraction
* BeautifulSoup: Library used for webscraping
* Pandas: Library used for data handling and cration of dataframes
* DODF Website: Website in which the DODFs are downloaded from

## Logical View
---------------

### Overview

DODFMiner is a library and CLI application made with the Python language, using MuPDF, BeautifulSoup, Pandas, and many others python libraries. The purpose of DODFMiner is to be an library and tool to fullfil the hole process of extraction of a official diary from federal district in Brazil. 


The objective of RasaNLU is to apply natural language algorithms to extract the user's intention (intents) and from Rasa Core it is possible to manage the dialogue between the user and the bot. The main functionality is the policy, which receives the user's intent, updates the tracker () and provides the best bot action (utter, action, listening). The Node.js platform is a runtime environment that executes JavaScript code for writing command-line tools and for server-side scripts, capable of performing asynchronous input / output, which allows other processing to continue before the transmission has ended.

The purpose of Amika is to be an application that facilitates communication and contact between professor, students and monitors of the discipline of Happiness offered at the University of Brasilia on the campus of Gama. From the PostgreSQL database, it will be possible to store student and class data, both student activities that will be delivered by students through the application and the basic data of each student in the academic environment.

### Package Diagram

### Class Diagram

### Use Cases


## References
-------------

https://fga-eps-mds.github.io/2019.2-Amika-Wiki/#/docs/projeto/documentoarquitetura

https://realpython.com/python-application-layouts/


