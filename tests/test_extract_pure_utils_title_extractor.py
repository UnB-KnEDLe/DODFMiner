import os
import re
import json
import pytest
import joblib
import inspect
from unittest.mock import patch
from pathlib import Path
from functools import reduce
import operator

import fitz
from dodfminer.extract.pure.utils import title_extractor
from dodfminer.extract.pure.utils.title_extractor import Box, BBox
from dodfminer.extract.pure.utils.title_extractor import TextTypeBboxPageTuple as Tuple


BASE_PATH = Path(
    ""+os.path.dirname(__file__)+"/support"
)

PDF_2020_PATH = BASE_PATH/'03-04-2020_marked.pdf'
PDF_2018_PATH = BASE_PATH/'03-12-2018 INTEGRA.pdf'
PDF_2017_PATH = BASE_PATH/'05-10-2017 INTEGRA.pdf'
PDF_2001_PATH = BASE_PATH/'6-12-2001_secao1.pdf'

BLOCKS_2001 = BASE_PATH/''
BOLD_UPPER_CONTENT = BASE_PATH/''

def jsdump(obj):
    """Simple wrapper for turning object into json.
    Its only purpose is to save some lines."""
    return json.dumps(obj, ensure_ascii=False)

def tuplefy(lis):
    """Turn iterables into tuples. Makes comparison easier."""
    try:
        return tuple([tuplefy(i) for i in lis])
    except:
        return tuple([tuple(i) for i in lis])


def stuplefy(lis):
    """Turn iterable tuple of tuples."""
    return tuple([tuple(i) for i in lis])

@pytest.fixture(scope='module')
def extractor_2001():
    return title_extractor.ExtractorTitleSubtitle(PDF_2001_PATH.as_posix())

@pytest.fixture(scope='module')
def extractor_2017():
    return title_extractor.ExtractorTitleSubtitle(PDF_2017_PATH.as_posix())

@pytest.fixture(scope='module')
def extractor_2018():
    return title_extractor.ExtractorTitleSubtitle(PDF_2018_PATH.as_posix())

@pytest.fixture(scope='module')
def extractor_2020():
    return title_extractor.ExtractorTitleSubtitle(PDF_2020_PATH.as_posix())





@pytest.fixture(scope='module')
def doc_2001():
    return fitz.open(PDF_2001_PATH)

@pytest.fixture(scope='module')
def doc_2017():
    return fitz.open(PDF_2017_PATH)

@pytest.fixture(scope='module')
def doc_2018():
    return fitz.open(PDF_2018_PATH)

@pytest.fixture(scope='module')
def doc_2020():
    return fitz.open(PDF_2020_PATH)

def test_load_blocks_list_1():
    functions_with_path('load_blocks_list', PDF_2001_PATH)

def test_load_blocks_list_2():
    functions_with_path('load_blocks_list', PDF_2017_PATH)

def test_load_blocks_list_3():
    functions_with_path('load_blocks_list', PDF_2018_PATH)

def test_load_blocks_list_4():
    functions_with_path('load_blocks_list', PDF_2020_PATH)


def functions_with_path(name, pdf_path):
    """Wrapper for member functions of title_extractor which
         expects to receive a `pathlib.Path` (indidicating a file path).
    """
    assert (
        jsdump(getattr(title_extractor, name)(pdf_path))
        == 
        jsdump(json.load(open(
            pdf_path.as_posix()[:-4] + '/' f'{name}.json'))
        )
    )

def functions_with_kargs(name, pdf_path, **kargs):
    """Wrapper for member functions of title_extractor which
         expects to receive a `pathlib.Path` (indidicating a file path).
    """
    assert (
        jsdump(getattr(title_extractor, name)(**kargs))
        == 
        jsdump(json.load(open(
            pdf_path.as_posix()[:-4] + '/' f'{name}.json'))
        )
    )


def functions_whole_doc(name, doc):
    assert (
        jsdump(getattr(title_extractor, name)(doc))
        == 
        jsdump(json.load(open(
            doc.name[:-4] + '/' f'{name}.json'))
        )
    )




@pytest.fixture(scope='module')
def elements_and_width():
    return ([
        BBox(Box(x0=100, y0=110, x1=150, y1=100)),
        BBox(Box(x0=200, y0=200, x1=150, y1=100)),
        BBox(Box(x0=300, y0=50, x1=150, y1=100)),
        BBox(Box(x0=400, y0=20, x1=150, y1=100)),

        BBox(Box(x0=500, y0=400, x1=150, y1=100)),
        BBox(Box(x0=600, y0=678, x1=150, y1=100)),
        BBox(Box(x0=700, y0=551, x1=150, y1=100)),
        BBox(Box(x0=800, y0=100, x1=150, y1=100)),
        BBox(Box(x0=900, y0=240, x1=150, y1=100)),
    ], 900)

@pytest.fixture()
def elements_expected():
    return [
        [        
            BBox(Box(x0=100, y0=110, x1=150, y1=100)),
            BBox(Box(x0=200, y0=200, x1=150, y1=100)),
            BBox(Box(x0=300, y0=50, x1=150, y1=100)),
            BBox(Box(x0=400, y0=20, x1=150, y1=100)),
        ],
        [
            BBox(Box(x0=500, y0=400, x1=150, y1=100)),
            BBox(Box(x0=600, y0=678, x1=150, y1=100)),
            BBox(Box(x0=700, y0=551, x1=150, y1=100)),
            BBox(Box(x0=800, y0=100, x1=150, y1=100)),
            BBox(Box(x0=900, y0=240, x1=150, y1=100)),        ],
    ]


def test_group_by_column(elements_and_width, elements_expected):
    grouped = title_extractor.group_by_column(*elements_and_width)
    assert stuplefy(grouped) == stuplefy(elements_expected)


@pytest.fixture()
def elements_page():
    return [
        Tuple('texto', None, None, 1),
        Tuple('outro texto', None, None, 2),
        Tuple('ficar junto com "texto"', None, None, 1),
        Tuple('tururu', None, None, 14),
        Tuple('just another text', None, None, 55),
        Tuple('KnEDLe rocks!', None, None, 3),
        Tuple('Grande Teo', None, None, 55),
        Tuple('>>> Vic', None, None, 3),
    ]

@pytest.fixture()
def elements_page_expected():
    return {
        1: [
            Tuple('texto', None, None, 1),
            Tuple('ficar junto com "texto"', None, None, 1),
        ],
        2: [
            Tuple('outro texto', None, None, 2),
        ],
        3: [
            Tuple('KnEDLe rocks!', None, None, 3),
            Tuple('>>> Vic', None, None, 3),
        ],
        14: [
            Tuple('tururu', None, None, 14),
        ],
        55: [
            Tuple('just another text', None, None, 55),
            Tuple('Grande Teo', None, None, 55),
        ],
    }

def test_group_by_page(elements_page, elements_page_expected):
    grouped = title_extractor.group_by_page(elements_page)
    assert (sorted(grouped.keys()) == sorted(elements_page_expected.keys())
            and json.dumps(elements_page_expected) == json.dumps(grouped)
    )


@pytest.fixture()
def elements_expected_sort():
    return reduce(operator.add, (
        [        
            BBox(Box(x0=400, y0=20, x1=150, y1=100)),
            BBox(Box(x0=300, y0=50, x1=150, y1=100)),
            BBox(Box(x0=100, y0=110, x1=150, y1=100)),
            BBox(Box(x0=200, y0=200, x1=150, y1=100)),
        ],
        [
            BBox(Box(x0=800, y0=100, x1=150, y1=100)),
            BBox(Box(x0=900, y0=240, x1=150, y1=100)),
            BBox(Box(x0=500, y0=400, x1=150, y1=100)),
            BBox(Box(x0=700, y0=551, x1=150, y1=100)),
            BBox(Box(x0=600, y0=678, x1=150, y1=100)),
        ]
    ))


def test_sort_by_column(elements_and_width, elements_expected_sort):
    sorted_ = title_extractor.sort_by_column( *elements_and_width )
    assert json.dumps(elements_expected_sort) == json.dumps(sorted_)


def test_invert_TextTypeBboxPageTuple_1():
    tup = Tuple('texto', title_extractor._TYPE_SUBTITLE, 123, 34)
    inv_tup = Tuple('texto', title_extractor._TYPE_TITLE, 123, 34)
    assert inv_tup == title_extractor._invert_TextTypeBboxPageTuple(tup)

def test_invert_TextTypeBboxPageTuple_2():
    tup = Tuple('nadaver', title_extractor._TYPE_TITLE, 123, 34)
    inv_tup = Tuple('nadaver', title_extractor._TYPE_SUBTITLE, 123, 34)
    assert inv_tup == title_extractor._invert_TextTypeBboxPageTuple(tup)

def test_invert_TextTypeBboxPageTuple_3():
    tup = Tuple('nadaver', title_extractor._TYPE_TITLE, 123, 34)
    inv_tup = Tuple('nadaperder', title_extractor._TYPE_SUBTITLE, 123, 34)
    assert inv_tup != title_extractor._invert_TextTypeBboxPageTuple(tup)


def test_extract_bold_upper_page():
    """ '_extract_bold_upper_page' will not be tested directly"""
    pass

def test_extract_bold_upper_pdf_1(doc_2001):
    functions_whole_doc('_extract_bold_upper_pdf', doc_2001)

def test_extract_bold_upper_pdf_2(doc_2017):
    functions_whole_doc('_extract_bold_upper_pdf', doc_2017)

def test_extract_bold_upper_pdf_3(doc_2018):
    functions_whole_doc('_extract_bold_upper_pdf', doc_2018)

def test_extract_bold_upper_pdf_4(doc_2020):
    functions_whole_doc('_extract_bold_upper_pdf', doc_2020)


def test_sort_2column():
    """ 'sort_2column' will not be tested directly.
    It is just a wrapper using `group_by_page` and `sort_by_column`
    """
    pass


def test_get_titles_subtitles():
    """Hard to test. It's indirectly tested by `test_get_titles_subtitles_smart_X`"""
    pass

def test_get_titles_subtitles_smart_1(doc_2001):
    functions_with_kargs(
        '_get_titles_subtitles_smart', PDF_2001_PATH, doc=doc_2001,
        width_lis = [p.MediaBox[2] for p in doc_2001],
    )
def test_get_titles_subtitles_smart_2(doc_2017):
    functions_with_kargs(
        '_get_titles_subtitles_smart', PDF_2017_PATH, doc=doc_2017,
        width_lis = [p.MediaBox[2] for p in doc_2017],
    )
def test_get_titles_subtitles_smart_3(doc_2018):
    functions_with_kargs(
        '_get_titles_subtitles_smart', PDF_2018_PATH, doc=doc_2018,
        width_lis = [p.MediaBox[2] for p in doc_2018],
    )
def test_get_titles_subtitles_smart_4(doc_2020):
    functions_with_kargs(
        '_get_titles_subtitles_smart', PDF_2020_PATH, doc=doc_2020,
        width_lis = [p.MediaBox[2] for p in doc_2020],
    )


def test_extract_titles_subtitles_1():
    functions_with_path('extract_titles_subtitles', PDF_2001_PATH)

def test_extract_titles_subtitles_2():
    functions_with_path('extract_titles_subtitles', PDF_2017_PATH)

def test_extract_titles_subtitles_3():
    functions_with_path('extract_titles_subtitles', PDF_2018_PATH)

def test_extract_titles_subtitles_4():
    functions_with_path('extract_titles_subtitles', PDF_2020_PATH)



def test_titles_1(extractor_2001):
    wrapper_extractor_props(extractor_2001, 'titles')

def test_titles_2(extractor_2017):
    wrapper_extractor_props(extractor_2017, 'titles')

def test_titles_3(extractor_2018):
    wrapper_extractor_props(extractor_2018, 'titles')

def test_titles_4(extractor_2020):
    wrapper_extractor_props(extractor_2020, 'titles')


def test_subtitles_1(extractor_2001):
    wrapper_extractor_props(extractor_2001, 'subtitles')

def test_subtitles_2(extractor_2017):
    wrapper_extractor_props(extractor_2017, 'subtitles')

def test_subtitles_3(extractor_2018):
    wrapper_extractor_props(extractor_2018, 'subtitles')

def test_subtitles_4(extractor_2020):
    wrapper_extractor_props(extractor_2020, 'subtitles')


def test_json_1(extractor_2001):
    wrapper_extractor_props(extractor_2001, 'json')

def test_json_2(extractor_2017):
    wrapper_extractor_props(extractor_2017, 'json')

def test_json_3(extractor_2018):
    wrapper_extractor_props(extractor_2018, 'json')

def test_json_4(extractor_2020):
    wrapper_extractor_props(extractor_2020, 'json')



def wrapper_extractor_props(extractor, name):
    ground_truth = json.dumps(json.load(
        open(Path(extractor._path[:-4])/f'{name}.json'))
    )
    hier = json.dumps(getattr(extractor, name))
    assert ground_truth == hier


def test_titles_subtitles_hierarchy_1(extractor_2001):
    wrapper_extractor_props(extractor_2001, 'titles_subtitles_hierarchy')

def test_titles_subtitles_hierarchy_2(extractor_2017):
    wrapper_extractor_props(extractor_2017, 'titles_subtitles_hierarchy')

def test_titles_subtitles_hierarchy_3(extractor_2018):
    wrapper_extractor_props(extractor_2018, 'titles_subtitles_hierarchy')


def test_titles_subtitles_hierarchy_4(extractor_2020):
    wrapper_extractor_props(extractor_2020, 'titles_subtitles_hierarchy')



def test_reset(extractor_2001):
    extractor_2001.reset()
    assert (not extractor_2001._json
            and not extractor_2001._hierarchy
            and not extractor_2001._cache
    )


