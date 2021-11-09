==========
Pure Utils
==========

.. warning::
    This documentation needs improvments by the code's author.

.. contents:: Table of Contents

Box Extactor
============

.. automodule:: dodfminer.extract.pure.utils.box_extractor
    :members:

.. autofunction:: dodfminer.extract.pure.utils.box_extractor._extract_page_lines_content

.. autofunction:: dodfminer.extract.pure.utils.box_extractor.get_doc_text_boxes

.. autofunction:: dodfminer.extract.pure.utils.box_extractor.get_doc_text_lines

.. autofunction:: dodfminer.extract.pure.utils.box_extractor._get_doc_img

.. autofunction:: dodfminer.extract.pure.utils.box_extractor.get_doc_img_boxes

Title Filter
============

.. automodule:: dodfminer.extract.pure.utils.title_filter
    :members:

Title Extactor
==============

.. automodule:: dodfminer.extract.pure.utils.title_extractor
    :members:

.. autofunction:: dodfminer.extract.pure.utils.title_extractor.load_blocks_list

.. autofunction:: dodfminer.extract.pure.utils.title_extractor.group_by_column

.. autofunction:: dodfminer.extract.pure.utils.title_extractor.group_by_page

.. autofunction:: dodfminer.extract.pure.utils.title_extractor.sort_by_column

.. autofunction:: dodfminer.extract.pure.utils.title_extractor._invert_TextTypeBboxPageTuple

.. autofunction:: dodfminer.extract.pure.utils.title_extractor._extract_bold_upper_page

.. autofunction:: dodfminer.extract.pure.utils.title_extractor._extract_bold_upper_pdf

.. autofunction:: dodfminer.extract.pure.utils.title_extractor.sort_2column

.. autofunction:: dodfminer.extract.pure.utils.title_extractor._get_titles_subtitles

.. autofunction:: dodfminer.extract.pure.utils.title_extractor._get_titles_subtitles_smart

.. autofunction:: dodfminer.extract.pure.utils.title_extractor.extract_titles_subtitles

.. autoclass:: dodfminer.extract.pure.utils.title_extractor.ExtractorTitleSubtitle
    :members:

.. automethod::dodfminer.extract.pure.utils.title_extractor.ExtractorTitleSubtitle.__init__

.. automethod::dodfminer.extract.pure.utils.title_extractor.ExtractorTitleSubtitle._mount_json

.. automethod::dodfminer.extract.pure.utils.title_extractor.ExtractorTitleSubtitle._mount_hierarchy

.. automethod::dodfminer.extract.pure.utils.title_extractor.ExtractorTitleSubtitle._do_cache

.. automethod::dodfminer.extract.pure.utils.title_extractor.ExtractorTitleSubtitle.titles

.. automethod::dodfminer.extract.pure.utils.title_extractor.ExtractorTitleSubtitle.subtitles

.. automethod::dodfminer.extract.pure.utils.title_extractor.ExtractorTitleSubtitle.titles_subtitles

.. automethod::dodfminer.extract.pure.utils.title_extractor.ExtractorTitleSubtitle.titles_subtitles_hierarchy

.. automethod::dodfminer.extract.pure.utils.title_extractor.ExtractorTitleSubtitle.dump_json

.. automethod::dodfminer.extract.pure.utils.title_extractor.ExtractorTitleSubtitle.reset

.. autofunction:: dodfminer.extract.pure.utils.title_extractor.gen_title_base

.. autofunction:: dodfminer.extract.pure.utils.title_extractor.gen_hierarchy_base

