import os

import bs4
from bs4 import BeautifulSoup

from src.supermat.supermat_tei_parser import get_children_list_grouped, get_sentences_nodes, get_paragraphs_nodes



def test_get_sentences_nodes_input_with_sentences_grouped():
    soup = BeautifulSoup(open(os.path.join(os.path.dirname(__file__), "test_data", 'test_sentences.xml')), 'xml')

    children = get_sentences_nodes(soup, grouped=True)

    assert len(children) == 4
    assert len(children[0]) == 1
    assert len(children[1]) == 2
    assert len(children[2]) == 1
    assert len(children[3]) == 1


def test_get_sentences_nodes_input_with_sentences_flatten():
    soup = BeautifulSoup(open(os.path.join(os.path.dirname(__file__), "test_data", 'test_sentences.xml')), 'xml')

    children = get_sentences_nodes(soup, grouped=False)

    assert len(children) == 5
    assert [type(c) for c in children] == 5 * [bs4.element.Tag]


def test_get_paragraph_nodes_input_with_paragraphs():
    soup = BeautifulSoup(open(os.path.join(os.path.dirname(__file__), "test_data", 'test_paragraphs.xml')), 'xml')

    children = get_paragraphs_nodes(soup)

    assert len(children) == 4
    assert [type(c) for c in children] == 4 * [bs4.element.Tag]


def test_get_children_sentences_input_with_paragraphs():
    soup = BeautifulSoup(open(os.path.join(os.path.dirname(__file__), "test_data", 'test_sentences.xml')), 'xml')

    children = get_children_list_grouped(soup, use_paragraphs=False)

    assert len(children) == 4
    assert len(children[0]) == 1
    assert len(children[1]) == 2
    assert len(children[2]) == 1
    assert len(children[3]) == 1
