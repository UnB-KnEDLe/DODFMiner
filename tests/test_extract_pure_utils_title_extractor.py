# pylint: disable=protected-access

import os
import json
from pathlib import Path
from functools import reduce
import operator
import pytest
import numpy as np

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


def stuplefy(lis):
    """Turn iterable tuple of tuples."""
    return tuple(tuple(i) for i in lis)


@pytest.fixture(scope='module', name='extractor_2001')
def fixture_extractor_2001():
    return title_extractor.ExtractorTitleSubtitle(PDF_2001_PATH.as_posix())


@pytest.fixture(scope='module', name='extractor_2017')
def fixture_extractor_2017():
    return title_extractor.ExtractorTitleSubtitle(PDF_2017_PATH.as_posix())


@pytest.fixture(scope='module', name='extractor_2018')
def fixture_extractor_2018():
    return title_extractor.ExtractorTitleSubtitle(PDF_2018_PATH.as_posix())


@pytest.fixture(scope='module', name='extractor_2020')
def fixture_extractor_2020():
    return title_extractor.ExtractorTitleSubtitle(PDF_2020_PATH.as_posix())


@pytest.fixture(scope='module', name='doc_2001')
def fixture_doc_2001():
    return fitz.open(PDF_2001_PATH)


@pytest.fixture(scope='module', name='doc_2017')
def fixture_doc_2017():
    return fitz.open(PDF_2017_PATH)


@pytest.fixture(scope='module', name='doc_2018')
def fixture_doc_2018():
    return fitz.open(PDF_2018_PATH)


@pytest.fixture(scope='module', name='doc_2020')
def fixture_doc_2020():
    return fitz.open(PDF_2020_PATH)


def test_load_blocks_list_1():
    functions_with_path_cmp_first_el('load_blocks_list', PDF_2001_PATH)


def test_load_blocks_list_2():
    functions_with_path_cmp_first_el('load_blocks_list', PDF_2017_PATH)


def test_load_blocks_list_3():
    functions_with_path_cmp_first_el('load_blocks_list', PDF_2018_PATH)


def test_load_blocks_list_4():
    functions_with_path_cmp_first_el('load_blocks_list', PDF_2020_PATH)

def functions_with_path(name, pdf_path):
    """Wrapper for member functions of title_extractor which
         expects to receive a `pathlib.Path` (indidicating a file path).
    """
    with open(pdf_path.as_posix()[:-4] + '/' f'{name}.json', encoding='utf-8') as json_file:
        generated_array = np.array(getattr(title_extractor, name)(pdf_path), dtype=object)
        ground_truth_array = np.array(json.load(json_file), dtype=object)

        # Asserting only extracted title/subtitle and its designated type
        assert (generated_array[:,:2] == ground_truth_array[:,:2]).all()
        # Asserting only page that title/subtitle was extracted from
        assert (generated_array[:,3] == ground_truth_array[:,3]).all()
        # These asserts ignore the block coordinates,
        # because the precision varies throughout the pymu versions.

def functions_with_path_cmp_first_el(name, pdf_path):
    """ Similar to functions_with_path but compares specific structure of the first elements
        ont the load_blocks_list dictionary attributes list
    """
    with open(pdf_path.as_posix()[:-4] + '/' f'{name}.json', encoding='utf-8') as json_file:
        assert jsdump(getattr(title_extractor, name)(pdf_path)[0][0]['lines'][0]['spans'][0]['text']) \
        == \
        jsdump(json.load(json_file)[0][0]['lines'][0]['spans'][0]['text'])

def functions_with_kargs(name, pdf_path, **kargs):
    """Wrapper for member functions of title_extractor which
         expects to receive a `pathlib.Path` (indidicating a file path).
    """
    with open(pdf_path.as_posix()[:-4] + '/' f'{name}.json', encoding='utf-8') as json_file:
        # Suppressing VisibleDeprecationWarning
        np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)

        generated_array = np.vstack(getattr(title_extractor, name)(**kargs))
        ground_truth_array = np.vstack(json.load(json_file))

        # Asserting only extracted title/subtitle and its designated type
        assert (generated_array[:,:2] == ground_truth_array[:,:2]).all()
        # Asserting only page that title/subtitle was extracted from
        assert (generated_array[:,3] == ground_truth_array[:,3]).all()
        # These asserts ignore the block coordinates,
        # because the precision varies throughout the pymu versions.

def functions_doc_bold_text(name, doc):
    desired_keys = ["text", "page"]

    select_key = lambda x: dict((key,value) for key, value in x.items() if key in desired_keys)
    select_dict_keys_on_list = lambda x:list(map(lambda page: list(map(select_key, page)), x))

    received = select_dict_keys_on_list(getattr(title_extractor, name)(doc))
    with open(doc.name[:-4] + '/' f'{name}.json', encoding='utf-8') as json_pointer:
        expected = select_dict_keys_on_list(json.load(json_pointer))

    assert (jsdump(received) == jsdump(expected))


@pytest.fixture(scope='module', name='elements_and_width')
def fixture_elements_and_width():
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


@pytest.fixture(name='elements_expected')
def fixture_elements_expected():
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
            BBox(Box(x0=900, y0=240, x1=150, y1=100)), ],
    ]


def test_group_by_column(elements_and_width, elements_expected):
    grouped = title_extractor.group_by_column(*elements_and_width)
    assert stuplefy(grouped) == stuplefy(elements_expected)


@pytest.fixture(name='elements_page')
def fixture_elements_page():
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


@pytest.fixture(name='elements_page_expected')
def fixture_elements_page_expected():
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


@pytest.fixture(name='elements_expected_sort')
def fixture_elements_expected_sort():
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
    sorted_ = title_extractor.sort_by_column(*elements_and_width)
    assert json.dumps(elements_expected_sort) == json.dumps(sorted_)


def test_invert_text_type_bbox_page_tuple_1():
    tup = Tuple('texto', title_extractor._TYPE_SUBTITLE, 123, 34)
    inv_tup = Tuple('texto', title_extractor._TYPE_TITLE, 123, 34)
    assert inv_tup == title_extractor.invert_text_type_bbox_page_tuple(tup)


def test_invert_text_type_bbox_page_tuple_2():
    tup = Tuple('nadaver', title_extractor._TYPE_TITLE, 123, 34)
    inv_tup = Tuple('nadaver', title_extractor._TYPE_SUBTITLE, 123, 34)
    assert inv_tup == title_extractor.invert_text_type_bbox_page_tuple(tup)


def test_invert_text_type_bbox_page_tuple_3():
    tup = Tuple('nadaver', title_extractor._TYPE_TITLE, 123, 34)
    inv_tup = Tuple('nadaperder', title_extractor._TYPE_SUBTITLE, 123, 34)
    assert inv_tup != title_extractor.invert_text_type_bbox_page_tuple(tup)


def test_extract_bold_upper_page():
    """ '_extract_bold_upper_page' will not be tested directly"""


def test_extract_bold_upper_pdf_1(doc_2001):
    functions_doc_bold_text('_extract_bold_upper_pdf', doc_2001)


def test_extract_bold_upper_pdf_2(doc_2017):
    functions_doc_bold_text('_extract_bold_upper_pdf', doc_2017)


def test_extract_bold_upper_pdf_3(doc_2018):
    functions_doc_bold_text('_extract_bold_upper_pdf', doc_2018)


def test_extract_bold_upper_pdf_4(doc_2020):
    functions_doc_bold_text('_extract_bold_upper_pdf', doc_2020)


def test_sort_2column():
    """ 'sort_2column' will not be tested directly.
    It is just a wrapper using `group_by_page` and `sort_by_column`
    """


def test_get_titles_subtitles():
    """Hard to test. It's indirectly tested by `test_get_titles_subtitles_smart_X`"""


def test_get_titles_subtitles_smart_1(doc_2001):
    functions_with_kargs(
        '_get_titles_subtitles_smart', PDF_2001_PATH, doc=doc_2001,
        width_lis=[p.MediaBox[2] for p in doc_2001],
    )


def test_get_titles_subtitles_smart_2(doc_2017):
    functions_with_kargs(
        '_get_titles_subtitles_smart', PDF_2017_PATH, doc=doc_2017,
        width_lis=[p.MediaBox[2] for p in doc_2017],
    )


def test_get_titles_subtitles_smart_3(doc_2018):
    functions_with_kargs(
        '_get_titles_subtitles_smart', PDF_2018_PATH, doc=doc_2018,
        width_lis=[p.MediaBox[2] for p in doc_2018],
    )


def test_get_titles_subtitles_smart_4(doc_2020):
    functions_with_kargs(
        '_get_titles_subtitles_smart', PDF_2020_PATH, doc=doc_2020,
        width_lis=[p.MediaBox[2] for p in doc_2020],
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
    with open(Path(extractor._path[:-4])/f'{name}.json', encoding='utf-8') as json_file:
        if name in ['titles', 'subtitles']:
            ground_truth = np.array(json.load(json_file), dtype=object)
            hier= np.array(getattr(extractor, name), dtype=object)

            assert (hier[:,:2] == ground_truth[:,:2]).all()
            assert (hier[:,3] == ground_truth[:,3]).all()
        else:
            ground_truth = json.dumps(json.load(json_file))
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
            and not extractor_2001._cached
            )
