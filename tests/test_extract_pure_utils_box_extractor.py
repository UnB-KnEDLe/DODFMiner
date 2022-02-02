# pylint: disable=protected-access

import os
import json
from pathlib import Path
import pytest
import fitz

from dodfminer.extract.pure.utils import box_extractor

BASE_PATH = Path(
    ""+os.path.dirname(__file__)+"/support"
)
PDF_PATH = BASE_PATH/'03-12-2018.pdf'
PAGE_ONE_LINES_PATH = BASE_PATH/'03-12-2018_pagina1_lines.json'
PAGE_49_LINES_PATH = BASE_PATH/'03-12-2018_pagina49_lines.json'
GET_DOC_TEXT_BOXES_PATH = BASE_PATH/'03-12-2018_get_doc_text_boxes.json'
GET_DOC_TEXT_LINES_PATH = BASE_PATH/'03-12-2018_get_doc_text_lines.json'
GET_DOC_IMG_PATH = BASE_PATH/'03-12-2018_get_doc_img.json'
GET_DOC_IMG_BOXES_PATH = BASE_PATH/'03-12-2018_get_doc_img_boxes.json'


def tuplefy(lis):
    """Turn iterables into tuples. Makes comparison easier."""
    try:
        return tuple(tuplefy(i) for i in lis)
    except TypeError:
        return tuple(tuple(i) for i in lis)


@pytest.fixture(scope='module', name='pdf_fitz')
def fixture_pdf_fitz():
    return fitz.open(PDF_PATH.as_posix())


def wrapper_extract_page_lines_content(pdf_fitz, page_num, path):
    # Can be a title
    as_tup = tuplefy(
        box_extractor._extract_page_lines_content(pdf_fitz[page_num])
    )
    with open(path, encoding='utf-8') as json_file:
        ground_truth = json.load(json_file)
        ground_truth = tuplefy(ground_truth)
        assert as_tup == ground_truth


def test_extract_page_lines_content_1(pdf_fitz):
    # Can be a title
    wrapper_extract_page_lines_content(
        pdf_fitz, 0, PAGE_ONE_LINES_PATH
    )


def test_extract_page_lines_content_49(pdf_fitz):
    # Can be a title
    wrapper_extract_page_lines_content(
        pdf_fitz, 48, PAGE_49_LINES_PATH
    )


def test_get_doc_text_boxes(pdf_fitz):
    assert len(box_extractor.get_doc_text_boxes(pdf_fitz)) == len(pdf_fitz)


def test_doc_text_lines(pdf_fitz):
    with open(GET_DOC_TEXT_LINES_PATH.as_posix(), encoding='utf-8') as json_file:
        ground_truth = json.load(json_file)
        assert (
            tuplefy(ground_truth)
            == tuplefy(box_extractor.get_doc_text_lines(pdf_fitz))
        )


def test_get_doc_img(pdf_fitz):
    with open(GET_DOC_IMG_PATH.as_posix(), encoding='utf-8') as json_file:
        ground_truth = json.load(json_file)
        assert (
            tuplefy(ground_truth)
            == tuplefy(box_extractor._get_doc_img(pdf_fitz))
        )


def test_get_doc_img_boxes(pdf_fitz):
    with open(GET_DOC_IMG_BOXES_PATH.as_posix(), encoding='utf-8') as json_file:
        ground_truth = json.load(json_file)
        assert (
            len(tuplefy(ground_truth))
            == len(tuplefy(box_extractor.get_doc_img_boxes(pdf_fitz)))
        )
