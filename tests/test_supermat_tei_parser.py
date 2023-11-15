import os

import bs4
from bs4 import BeautifulSoup

from src.supermat.supermat_tei_parser import get_nodes, process_paragraphs, process_file_to_json


def test_get_sentences_nodes_input_with_sentences_grouped():
    soup = BeautifulSoup(open(os.path.join(os.path.dirname(__file__), "test_data", 'test_sentences.xml')), 'xml')

    children = get_nodes(soup, group_by_paragraph=True)

    assert len(children) == 4
    assert len(children[0]) == 1
    assert len(children[1]) == 2
    assert len(children[2]) == 1
    assert len(children[3]) == 1


def test_get_sentences_nodes_input_with_sentences_flatten():
    soup = BeautifulSoup(open(os.path.join(os.path.dirname(__file__), "test_data", 'test_sentences.xml')), 'xml')

    children = get_nodes(soup, group_by_paragraph=False)

    assert len(children) == 5
    assert [type(c) for c in children] == 5 * [bs4.element.Tag]


def test_get_nodes_with_input_sentences_grouped_get_paragraphs():
    soup = BeautifulSoup(open(os.path.join(os.path.dirname(__file__), "test_data", 'test_sentences.xml')), 'xml')

    children = get_nodes(soup, use_paragraphs=True)

    assert len(children) == 4
    assert len(children[0]) == 1
    assert len(children[1]) == 5
    assert len(children[2]) == 3
    assert len(children[2]) == 3


def test_get_paragraph_nodes_input_with_paragraphs():
    soup = BeautifulSoup(open(os.path.join(os.path.dirname(__file__), "test_data", 'test_paragraphs.xml')), 'xml')

    children = get_nodes(soup, use_paragraphs=True)

    assert len(children) == 4
    assert [type(c) for c in children] == 4 * [bs4.element.Tag]


def test_process_paragraphs_input_paragraphs():
    file_path = os.path.join(os.path.dirname(__file__), "test_data", 'test_paragraphs.xml')

    with open(file_path, encoding='utf-8') as fp:
        doc = fp.read()

    soup = BeautifulSoup(doc, 'xml')

    paragraph_nodes = get_nodes(soup, use_paragraphs=True)
    passages, relations = process_paragraphs(paragraph_nodes)

    assert len(passages) == 4
    title = passages[0]
    assert title['section'] == "title"
    assert title['type'] == "paragraph"
    assert len(title['tokens']) == 1
    assert title['text'] == "Test"

    abstract = passages[1]
    assert abstract['section'] == "abstract"
    assert abstract['type'] == "paragraph"
    assert len(abstract['tokens']) == 3
    assert abstract['text'] == "Paragraph 1"


def test_process_paragraphs_input_sentences():
    file_path = os.path.join(os.path.dirname(__file__), "test_data", 'test_sentences.xml')

    with open(file_path, encoding='utf-8') as fp:
        doc = fp.read()

    soup = BeautifulSoup(doc, 'xml')

    paragraph_nodes = get_nodes(soup, use_paragraphs=True)
    passages, relations = process_paragraphs(paragraph_nodes)

    assert len(passages) == 4
    title = passages[0]
    assert title['section'] == "title"
    assert title['type'] == "paragraph"
    assert len(title['tokens']) == 1
    assert title['text'] == "Test"

    abstract = passages[1]
    assert abstract['section'] == "abstract"
    assert abstract['type'] == "paragraph"
    assert abstract['text'] == "Sentence 1. Sentence 2."
    assert len(abstract['tokens']) == 9

    abstract = passages[2]
    assert abstract['section'] == "body"
    assert abstract['type'] == "paragraph"
    assert abstract['text'] == "Sentence 3."
    assert len(abstract['tokens']) == 4

    abstract = passages[3]
    assert abstract['section'] == "figureCaption"
    assert abstract['type'] == "paragraph"
    assert len(abstract['tokens']) == 4
    assert abstract['text'] == "Sentence 4."


def test_process_paragraphs_input_sentences_2():
    file_path = os.path.join(os.path.dirname(__file__), "test_data", 'test_body1.xml')

    with open(file_path, encoding='utf-8') as fp:
        doc = fp.read()

    soup = BeautifulSoup(doc, 'xml')

    paragraph_nodes = get_nodes(soup, use_paragraphs=True)
    passages, relations = process_paragraphs(paragraph_nodes)

    assert len(passages) == 2

    first = passages[0]
    assert len(first['spans']) == 4

    second = passages[1]
    assert len(second['spans']) == 6


def test_process_file():
    file_path = os.path.join(os.path.dirname(__file__), "test_data", 'kotesample.xml')

    json = process_file_to_json(file_path)

    span_map = {}

    passages = json['passages']
    for passage in passages:
        for span in passage['spans']:
            if 'id' in span:
                if span['id'] not in span_map:
                    span_map[span['id']] = span
                else:
                    print("error")

    assert len(span_map.keys()) == 8

    relations = json['relations']

    assert len(relations) == 8
