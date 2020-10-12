import os
import re
import json
import pytest
import joblib
import sklearn_crfsuite
from unittest.mock import patch
from pathlib import Path

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
        return tuple([tuplefy(i) for i in lis])
    except:
        return tuple([tuple(i) for i in lis])

@pytest.fixture(scope='module')
def pdf_fitz():
    return fitz.open(PDF_PATH.as_posix())

def wrapper_extract_page_lines_content(pdf_fitz, page_num, path):
    # Can be a title
    as_tup = tuplefy(
        box_extractor._extract_page_lines_content(pdf_fitz[page_num])
    )
    ground_truth = json.load(open(path))
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
    ground_truth = json.load(
        open(GET_DOC_TEXT_BOXES_PATH.as_posix())
    )
    assert (
        tuplefy(ground_truth) 
        == tuplefy(box_extractor.get_doc_text_boxes(pdf_fitz))
    )


def test_doc_text_lines(pdf_fitz):
    ground_truth = json.load(
        open(GET_DOC_TEXT_LINES_PATH.as_posix())
    )
    assert (
        tuplefy(ground_truth) 
        == tuplefy(box_extractor.get_doc_text_lines(pdf_fitz))
    )


def test_get_doc_img(pdf_fitz):
    ground_truth = json.load(
        open(GET_DOC_IMG_PATH.as_posix())
    )
    assert (
        tuplefy(ground_truth) 
        == tuplefy(box_extractor._get_doc_img(pdf_fitz))
    )


def test_get_doc_img(pdf_fitz):
    ground_truth = json.load(
        open(GET_DOC_IMG_PATH.as_posix())
    )
    assert (
        tuplefy(ground_truth) 
        == tuplefy(box_extractor._get_doc_img(pdf_fitz))
    )


def test_get_doc_img_boxes(pdf_fitz):
    ground_truth = json.load(
        open(GET_DOC_IMG_BOXES_PATH.as_posix())
    )
    assert (
        tuplefy(ground_truth) 
        == tuplefy(box_extractor.get_doc_img_boxes(pdf_fitz))
    )


