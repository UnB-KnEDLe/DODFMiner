===============
Downloader Core
===============

.. contents:: Table of Contents

.. automodule:: dodfminer.downloader.core

Downloader Class
================

.. autoclass:: dodfminer.downloader.core.Downloader
    :members:

Downloader Private Methods
==========================

One does not access directly none of those methods, but they are listed here in case the programmer
using the downloader library needs more informations.

Path Handling 
-------------

Methods that handle the creation of the paths to the dowloaded DODFS.

.. automethod:: dodfminer.downloader.core.Downloader._create_single_folder

.. automethod:: dodfminer.downloader.core.Downloader._create_download_folder

.. automethod:: dodfminer.downloader.core.Downloader._make_month_path

URL Making
----------

Methods that construct an URL to further make the download request.

.. automethod:: dodfminer.downloader.core.Downloader._make_url

.. automethod:: dodfminer.downloader.core.Downloader._make_href_url

.. automethod:: dodfminer.downloader.core.Downloader._make_download_url

Web Requests
------------

Methods that handle the download request and its execution.

.. automethod:: dodfminer.downloader.core.Downloader._fail_request_message
    
.. automethod:: dodfminer.downloader.core.Downloader._get_soup_link

.. automethod:: dodfminer.downloader.core.Downloader._download_pdf 

Others
------

Other methods for the downloader library.

.. automethod:: dodfminer.downloader.core.Downloader._string_to_date

.. automethod:: dodfminer.downloader.core.Downloader._file_exist

.. automethod:: dodfminer.downloader.core.Downloader._log