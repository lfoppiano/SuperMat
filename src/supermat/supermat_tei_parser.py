import re
from collections import OrderedDict
from pathlib import Path
from typing import Union, List

from bs4 import BeautifulSoup, Tag, NavigableString

from supermat.grobid_tokenizer import tokenizeSimple


def tokenise(string):
    return tokenizeSimple(string)


def get_section(tag: Tag):
    section = None
    if tag.name == 'p':
        section = tag.parent.name
    elif tag.name == 'ab':
        if 'type' in tag.attrs:
            type_ = tag.attrs['type']
            if type_ == 'keywords':
                section = "keywords"
            elif type_ == 'figureCaption':
                section = 'figureCaption'
            elif type_ == 'tableCaption':
                section = 'tableCaption'
    elif tag.name == 'title':
        section = 'title'

    return section


def process_file_to_json(input_file_path, use_paragraphs=False):
    with open(input_file_path, encoding='utf-8') as fp:
        doc = fp.read()

    mod_tags = re.finditer(r'(</\w+>) ', doc)
    for mod in mod_tags:
        doc = doc.replace(mod.group(), ' ' + mod.group(1))
    soup = BeautifulSoup(doc, 'xml')

    output_document = OrderedDict()
    output_document['doc_key'] = Path(str(input_file_path)).name
    output_document['dataset'] = 'SuperMat'
    output_document['lang'] = 'en'

    if use_paragraphs:
        output_document['level'] = 'paragraph'
        paragraph_nodes = get_nodes(soup, use_paragraphs=True)
        passages, relations = process_paragraphs(paragraph_nodes)
    else:
        output_document['level'] = 'sentence'
        sentence_nodes = get_nodes(soup, group_by_paragraph=True)
        passages, relations = process_sentences(sentence_nodes)

    output_document['passages'] = passages
    output_document['relations'] = relations

    return output_document


def process_paragraphs(paragraph_list: list) -> [List, List]:
    """
    Process XML with <p> and <s> as sentences.

    Return two list passage (sentence or paragraph,spans and link) and relations (links at document-level)
    """
    token_offset_sentence = 0
    ient = 1

    passages = []
    relations = []

    dic_dest_relationships = {}
    dic_source_relationships = {}
    linked_entity_registry = {}

    i = 0
    for paragraph_id, paragraph in enumerate(paragraph_list):
        passage = OrderedDict()

        j = 0
        offset = 0
        tokens = []
        text_paragraph = ''
        spans = []
        section = get_section(paragraph)

        passage['section'] = section
        passage['text'] = text_paragraph
        passage['tokens'] = tokens
        passage['type'] = 'paragraph'
        passage['spans'] = spans
        passage['id'] = paragraph_id

        for idx, item in enumerate(paragraph.contents):
            if type(item) is NavigableString:
                local_text = str(item).replace("\n", " ")
                # We preserve spaces that are in the middle
                if idx == 0 or idx == len(paragraph.contents) - 1:
                    local_text = local_text.strip()
                text_paragraph += local_text
                token_list = tokenise(local_text)
                tokens.extend(token_list)
                token_offset_sentence += len(token_list)
                offset += len(local_text)
            elif type(item) is Tag and item.name == 'rs':
                local_text = item.text
                text_paragraph += local_text
                span = OrderedDict()
                front_offset = 0
                if local_text.startswith(" "):
                    front_offset = len(local_text) - len(local_text.lstrip(" "))

                span['text'] = local_text.strip(" ")
                span['offset_start'] = offset + front_offset
                span['offset_end'] = offset + len(span['text']) + front_offset
                spans.append(span)

                offset += len(local_text)

                assert text_paragraph[span['offset_start']:span['offset_end']] == span['text']

                if 'type' not in item.attrs:
                    raise Exception("RS without type is invalid. Stopping")
                token_list = tokenise(local_text)
                tokens.extend(token_list)

                entity_class = item.attrs['type']
                span['type'] = entity_class

                span['token_start'] = token_offset_sentence
                span['token_end'] = token_offset_sentence + len(token_list) - 1

                # ner_entity = [token_offset_sentence, token_offset_sentence + len(token_list) - 1, label]
                # ner_sentence.append(ner_entity)

                if len(item.attrs) > 0:
                    ## multiple entities can point ot the same one, so "corresp" value can be duplicated
                    allow_duplicates = False
                    span_id = None
                    if 'xml:id' in item.attrs:
                        span['id'] = item['xml:id']
                        if item.attrs['xml:id'] not in dic_dest_relationships:
                            dic_dest_relationships[item.attrs['xml:id']] = [i + 1, j + 1, ient, entity_class]

                    if 'corresp' in item.attrs:
                        if 'id' not in span or span['id'] == "":
                            id_str = str(i + 1) + "," + str(j + 1)
                            span['id'] = get_hash(id_str)
                            if span['id'] not in dic_source_relationships:
                                dic_source_relationships[span['id']] = [item.attrs['corresp'].replace('#', ''),
                                                                        ient,
                                                                        entity_class]
                        else:
                            if span['id'] not in dic_source_relationships:
                                dic_source_relationships[span['id']] = [item.attrs['corresp'].replace('#', ''),
                                                                        ient,
                                                                        entity_class]

                        allow_duplicates = True

                    if 'id' in span:
                        if span['id'] not in linked_entity_registry.keys():
                            linked_entity_registry[span['id']] = span
                        else:
                            if not allow_duplicates:
                                print("The same key exists... something's wrong: ", span_id)

                j += 1

            ient += 1  # entity No.

        passage['text'] = text_paragraph
        passages.append(passage)
        i += 1

    for id__ in dic_source_relationships:
        destination_xml_id = dic_source_relationships[id__][0]

        for des in destination_xml_id.split(","):
            dict_coordinates = get_hash(id__)

            span_destination = linked_entity_registry[des]
            span_source = linked_entity_registry[dict_coordinates]
            link_source = {
                "targetId": span_destination['id'],
                "targetText": span_destination['text'],
                "targetType": span_destination['type']
            }

            link_destination = {
                "targetId": span_source['id'],
                "targetText": span_source['text'],
                "targetType": span_source['type']
            }

            relations.append({
                "source": link_source,
                "destination": link_destination
            })

            if 'links' in span_source:
                span_source['links'].append(link_source)
            else:
                span_source['links'] = [link_source]

            if 'links' in span_destination:
                span_destination['links'].append(link_destination)
            else:
                span_destination['links'] = [link_destination]

    return passages, relations


def process_sentences(sentences_grouped_by_paragraphs: list) -> [List, List]:
    """
    Process XML with <p> and <s> as sentences.

    Return two list passage (sentence or paragraph,spans and link) and relations (links at document-level)
    """
    token_offset_sentence = 0
    ient = 1

    passages = []
    relations = []

    dic_dest_relationships = {}
    dic_source_relationships = {}
    linked_entity_registry = {}

    i = 0
    for paragraph_id, paragraph in enumerate(sentences_grouped_by_paragraphs):
        for sentence_id, sentence in enumerate(paragraph):
            passage = OrderedDict()

            j = 0
            offset = 0
            tokens = []
            text_sentence = ''
            spans = []
            section = get_section(sentence)

            if not section:
                section = get_section(sentence.parent)

            passage['section'] = section
            passage['text'] = text_sentence
            passage['tokens'] = tokens
            passage['type'] = 'sentence'
            passage['spans'] = spans
            passage['group_id'] = paragraph_id
            passage['id'] = sentence_id

            for item in sentence.contents:
                if type(item) == NavigableString:
                    local_text = str(item)
                    text_sentence += local_text
                    token_list = tokenise(item.string)

                    # if len(token_list) > 0 and token_list[0] == ' ':  # remove space after tags
                    #     del token_list[0]

                    tokens.extend(token_list)
                    token_offset_sentence += len(token_list)
                    offset += len(local_text)

                elif type(item) is Tag and item.name == 'rs':
                    local_text = item.text
                    text_sentence += local_text
                    span = OrderedDict()
                    front_offset = 0
                    if local_text.startswith(" "):
                        front_offset = len(local_text) - len(local_text.lstrip(" "))

                    span['text'] = local_text.strip(" ")
                    span['offset_start'] = offset + front_offset
                    span['offset_end'] = offset + len(span['text']) + front_offset
                    spans.append(span)

                    offset += len(local_text)

                    assert text_sentence[span['offset_start']:span['offset_end']] == span['text']

                    if 'type' not in item.attrs:
                        raise Exception("RS without type is invalid. Stopping")
                    token_list = tokenise(local_text)
                    tokens.extend(token_list)

                    entity_class = item.attrs['type']
                    span['type'] = entity_class

                    span['token_start'] = token_offset_sentence
                    span['token_end'] = token_offset_sentence + len(token_list) - 1

                    # ner_entity = [token_offset_sentence, token_offset_sentence + len(token_list) - 1, label]
                    # ner_sentence.append(ner_entity)

                    if len(item.attrs) > 0:
                        ## multiple entities can point ot the same one, so "corresp" value can be duplicated
                        allow_duplicates = False
                        span_id = None
                        if 'xml:id' in item.attrs:
                            span['id'] = item['xml:id']
                            if item.attrs['xml:id'] not in dic_dest_relationships:
                                dic_dest_relationships[item.attrs['xml:id']] = [i + 1, j + 1, ient, entity_class]

                        if 'corresp' in item.attrs:
                            if 'id' not in span or span['id'] == "":
                                id_str = str(i + 1) + "," + str(j + 1)
                                span['id'] = get_hash(id_str)
                                if span['id'] not in dic_source_relationships:
                                    dic_source_relationships[span['id']] = [item.attrs['corresp'].replace('#', ''),
                                                                            ient,
                                                                            entity_class]
                            else:
                                if span['id'] not in dic_source_relationships:
                                    dic_source_relationships[span['id']] = [item.attrs['corresp'].replace('#', ''),
                                                                            ient,
                                                                            entity_class]

                            allow_duplicates = True

                        if 'id' in span:
                            if span['id'] not in linked_entity_registry.keys():
                                linked_entity_registry[span['id']] = span
                            else:
                                if not allow_duplicates:
                                    print("The same key exists... something's wrong: ", span_id)

                    j += 1

                ient += 1  # entity No.

            # token_offset_sentence += 1  # return

            passage['text'] = text_sentence
            # sentences.append(tokens_sentence)
            # ner.append(ner_sentence)
            passages.append(passage)
            i += 1

    for id__ in dic_source_relationships:
        destination_xml_id = dic_source_relationships[id__][0]

        for des in destination_xml_id.split(","):
            dict_coordinates = get_hash(id__)

            span_destination = linked_entity_registry[des]
            span_source = linked_entity_registry[dict_coordinates]
            link_source = {
                "targetId": span_destination['id'],
                "targetText": span_destination['text'],
                "targetType": span_destination['type']
            }

            link_destination = {
                "targetId": span_source['id'],
                "targetText": span_source['text'],
                "targetType": span_source['type']
            }

            relations.append({
                "source": link_source,
                "destination": link_destination
            })

            if 'links' in span_source:
                span_source['links'].append(link_source)
            else:
                span_source['links'] = [link_source]

            if 'links' in span_destination:
                span_destination['links'].append(link_destination)
            else:
                span_destination['links'] = [link_destination]

    return passages, relations


def get_nodes(soup, group_by_paragraph=True, use_paragraphs=False) -> Union[List, List[List]]:
    tags_title = []
    tags_text = []
    tags_captions = []

    paragraph_tag = "p"
    sentence_tag = "s"

    for child in soup.tei.children:
        if child.name == 'teiHeader':
            tags_title.extend([paragraph for paragraph in child.find_all("title")])
            tags_text.extend([paragraph for subchildren in child.find_all("abstract") for paragraph in
                              subchildren.find_all(paragraph_tag)])
            tags_text.extend([paragraph for paragraph in child.find_all("ab", {"type": "keywords"})])

        elif child.name == 'text':
            tags_text.extend([paragraph for subchildren in child.find_all("body") for paragraph in
                              subchildren.find_all(paragraph_tag)])
            tags_captions.extend([paragraph for paragraph in child.find_all("ab")])

    if use_paragraphs:
        for top_tag in tags_text + tags_captions:
            inside_sentences = top_tag.find_all("s")
            if len(inside_sentences) > 0:
                ic = 0
                for element in top_tag.children:
                    if isinstance(element, NavigableString):
                        new_element = element.replace("\n", " ")
                        element.replace_with(NavigableString(new_element))
                        ic += 1
                    elif element in inside_sentences:
                        for content_item in element.contents.copy():
                            top_tag.insert(ic, content_item.extract())
                            ic += 1
                        element.decompose()

        data_grouped = tags_title + tags_text + tags_captions
    else:
        data_grouped = [tags_title] + [[z for z in y.find_all(sentence_tag)] for y in tags_text + tags_captions]

        if not group_by_paragraph:
            data_flattened = [sentence for paragraph in data_grouped for sentence in paragraph]
            return data_flattened

    return data_grouped


def get_children_list(soup, use_paragraphs=False, verbose=False):
    children = []

    child_name = "p" if use_paragraphs else "s"
    for child in soup.tei.children:
        if child.name == 'teiHeader':
            pass
            children.append(child.find_all("title"))
            children.extend([subchild.find_all(child_name) for subchild in child.find_all("abstract")])
            children.extend([subchild.find_all(child_name) for subchild in child.find_all("ab", {"type": "keywords"})])
        elif child.name == 'text':
            children.extend([subchild.find_all(child_name) for subchild in child.find_all("body")])

    if verbose:
        print(str(children))

    return children


def get_relationship_name(source_label, destination_label):
    return source_label + "-" + destination_label


def get_hash(dict_coordinates_str):
    return dict_coordinates_str
    # return hashlib.md5(dict_coordinates_str.encode('utf-8')).hexdigest()
