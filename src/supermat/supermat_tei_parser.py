import re
from collections import OrderedDict
from pathlib import Path
from typing import Union, List

from bs4 import BeautifulSoup, Tag, NavigableString

from supermat.grobid_tokenizer import tokenizeSimple


def tokenise(string):
    return tokenizeSimple(string)


def get_section(pTag):
    section = None
    if pTag.name == 'p':
        section = pTag.parent.name
    elif pTag.name == 'ab':
        if 'type' in pTag.attrs:
            type = pTag.attrs['type']
            if type == 'keywords':
                section = "keywords"
            elif type == 'figureCaption':
                section = 'figureCaption'
            elif type == 'tableCaption':
                section = 'tableCaption'
    elif pTag.name == 'title':
        section = 'title'

    return section


def process_file(input_document, use_paragraphs=False):
    with open(input_document, encoding='utf-8') as fp:
        doc = fp.read()

    mod_tags = re.finditer(r'(</\w+>) ', doc)
    for mod in mod_tags:
        doc = doc.replace(mod.group(), ' ' + mod.group(1))
    soup = BeautifulSoup(doc, 'xml')

    children = get_children_list(soup, verbose=False, use_paragraphs=use_paragraphs)

    off_token = 0
    dic_token = {}
    ient = 1

    # list containing text and the dictionary with all the annotations
    paragraphs = []
    dic_dest_relationships = {}
    dic_source_relationships = {}

    i = 0
    for child in children:
        for pTag in child:
            j = 0
            section = get_section(pTag)
            if not section:
                section = get_section(pTag.parent)
            paragraphText = ''
            for item in pTag.contents:
                if type(item) == NavigableString:
                    paragraphText += str(item)

                    token_list = tokenise(item.string)
                    if token_list[0] == ' ':  # remove space after tags
                        del token_list[0]

                    entity_class = '_'

                    for token in token_list:
                        s = off_token
                        off_token += len(token.rstrip(' '))
                        e = off_token
                        if token.rstrip(' '):
                            dic_token[(i + 1, j + 1)] = [
                                s, e, token.rstrip(' '), section + f'[{i + 10000}]', entity_class, entity_class,
                                entity_class, entity_class, entity_class]
                            #                     print((i+1, j+1), s, e, [token], len(token.rstrip(' ')), off_token)
                            j += 1
                        if len(token) > 0 and token[-1] == ' ':
                            off_token += 1  #
                elif type(item) is Tag and item.name == 'rs':
                    paragraphText += item.text

                    token_list = tokenise(item.string)
                    #                 token_list[-1] += ' ' # add space the end of tag contents
                    if 'type' not in item.attrs:
                        raise Exception("RS without type is invalid. Stopping")

                    entity_class = item.attrs['type']
                    link_name = '_'
                    link_location = '_'

                    if len(item.attrs) > 0:
                        if 'xml:id' in item.attrs:
                            if item.attrs['xml:id'] not in dic_dest_relationships:
                                dic_dest_relationships[item.attrs['xml:id']] = [i + 1, j + 1, ient, entity_class]

                        if 'corresp' in item.attrs:
                            if (i + 1, j + 1) not in dic_source_relationships:
                                dic_source_relationships[i + 1, j + 1] = [item.attrs['corresp'].replace('#', ''),
                                                                          ient,
                                                                          entity_class]

                            # link_to = dic_relationships[item.attrs['ptr'].replace("#", '')]
                            # relationship_name = link_to[2] + '-' + entity
                            # relationship_references = str(link_to[0]) + '-' + str(link_to[1]) + '[' + str(
                            #     i + 1) + '-' + str(j + 1) + ']'
                            # print(dic_token[link_to[0], link_to[1]])
                        link_name = 'link_name'
                        link_location = 'link_location'

                    entity_class = entity_class.replace("_", "\\_")

                    for token in token_list:
                        s = off_token
                        off_token += len(token.rstrip(' '))
                        e = off_token
                        if token.rstrip(' '):
                            dic_token[(i + 1, j + 1)] = [s, e, token.rstrip(' '), section + f'[{i + 10000}]',
                                                         f'*[{ient}]',
                                                         entity_class + f'[{ient}]', link_name, link_location]
                            #                     print((i+1, j+1), s, e, [token], len(token.rstrip(' ')), off_token)
                            j += 1
                        if len(token) > 0 and token[-1] == ' ':
                            off_token += 1  #
                    ient += 1  # entity No.

            off_token += 1  # return

            paragraphs.append((i, paragraphText))
            i += 1

    for par_num, token_num in dic_source_relationships:
        destination_xml_id = dic_source_relationships[par_num, token_num][0]
        source_entity_id = dic_source_relationships[par_num, token_num][1]
        label = dic_source_relationships[par_num, token_num][2]

        # destination_xml_id: Use this to pick up information from dic_dest_relationship

        for des in destination_xml_id.split(","):
            destination_item = dic_dest_relationships[str(des)]
            destination_paragraph_tsv = destination_item[0]
            destination_token_tsv = destination_item[1]
            destination_entity_id = destination_item[2]
            destination_type = destination_item[3]

            relationship_name = get_relationship_name(label, destination_type)

            dict_coordinates = (destination_paragraph_tsv, destination_token_tsv)

            dic_token_entry = dic_token[dict_coordinates]
            if dic_token_entry[6] == 'link_name' and dic_token_entry[7] == 'link_location':
                dic_token_entry[6] = relationship_name
                dic_token_entry[7] = str(par_num) + '-' + str(token_num) + "[" + str(
                    source_entity_id) + '_' + str(destination_entity_id) + ']'
            else:
                dic_token_entry[6] += '|' + relationship_name
                dic_token_entry[7] += '|' + str(par_num) + '-' + str(token_num) + "[" + str(
                    source_entity_id) + '_' + str(destination_entity_id) + ']'

    # Cleaning up the dictionary token
    for k, v in dic_token.items():
        v[6] = v[6].replace('link_name', '_')
        v[7] = v[7].replace('link_location', '_')

    return paragraphs, dic_token


def process_file_to_json(finput, use_paragraphs=False):
    with open(finput, encoding='utf-8') as fp:
        doc = fp.read()

    mod_tags = re.finditer(r'(</\w+>) ', doc)
    for mod in mod_tags:
        doc = doc.replace(mod.group(), ' ' + mod.group(1))
    soup = BeautifulSoup(doc, 'xml')

    output_document = OrderedDict()
    output_document['doc_key'] = Path(str(finput)).name
    output_document['dataset'] = 'SuperMat'

    if use_paragraphs:
        paragraph_nodes = get_paragraphs_nodes(soup)
        passages, ner, relations = process_paragraphs(paragraph_nodes)
    else:
        sentence_nodes = get_sentences_nodes(soup, grouped=True)
        passages, ner, relations = process_sentences(sentence_nodes)

    output_document['passages'] = passages
    output_document['ner'] = ner
    output_document['relations'] = relations

    return output_document


def process_paragraphs(children: list) -> [List, List, List]:
    """Process paragraphs. If the XML contains Sentences, it aggregates them separated by a space. """
    token_offset_sentence = 0
    ient = 1

    # list containing text and the dictionary with all the annotations
    paragraphs = []
    ner = []
    relations = []

    i = 0
    for paragraph in children:
        j = 0
        text_paragraph = ''
        tokens_paragraph = []
        ner_sentence = []
        relations_sentence = []
        dic_dest_relationships = {}
        dic_source_relationships = {}
        linked_entity_registry = {}
        token_offset_sentence = 0

        first = True
        for sentence in paragraph:
            if not first:
                if len(text_paragraph) > 0:
                    text_paragraph += " "
                    tokens_paragraph.append(" ")
                    token_offset_sentence += 1
            if first:
                first = False

            for item in sentence.contents:
                if type(item) == NavigableString:
                    local_text = str(item)
                    text_paragraph += local_text

                    token_list = tokenise(item.string)
                    if len(token_list) > 0 and token_list[0] == ' ':  # remove space after tags
                        del token_list[0]
                        token_offset_sentence -= 1

                    tokens_paragraph.extend(token_list)
                    token_offset_sentence += len(token_list)

                elif type(item) is Tag and item.name == 'rs':
                    local_text = item.text
                    text_paragraph += local_text
                    if 'type' not in item.attrs:
                        raise Exception("RS without type is invalid. Stopping")
                    label = item.attrs['type']
                    token_list = tokenise(local_text)
                    tokens_paragraph.extend(token_list)

                    ner_entity = [token_offset_sentence, token_offset_sentence + len(token_list), label]
                    ner_sentence.append(ner_entity)

                    if len(item.attrs) > 0:
                        ## multiple entities can point ot the same one, so "corresp" value can be duplicated
                        allow_duplicates = False
                        span_id = None
                        if 'xml:id' in item.attrs:
                            span_id = item['xml:id']
                            if item.attrs['xml:id'] not in dic_dest_relationships:
                                dic_dest_relationships[item.attrs['xml:id']] = [i + 1, j + 1, ient, label]

                        if 'corresp' in item.attrs:
                            if span_id is None or span_id == "":
                                id_str = str(i + 1) + "," + str(j + 1)
                                span_id = get_hash(id_str)
                                if span_id not in dic_source_relationships:
                                    dic_source_relationships[span_id] = [item.attrs['corresp'].replace('#', ''),
                                                                         ient,
                                                                         label]
                            else:
                                if span_id not in dic_source_relationships:
                                    dic_source_relationships[span_id] = [item.attrs['corresp'].replace('#', ''),
                                                                         ient,
                                                                         label]

                            allow_duplicates = True

                        if span_id is not None:
                            if span_id not in linked_entity_registry.keys():
                                linked_entity_registry[span_id] = ner_entity
                            else:
                                if not allow_duplicates:
                                    print("The same key exists... something's wrong: ", span_id)

                    token_offset_sentence += len(token_list)

                    j += 1

                ient += 1  # entity No.

            # token_offset_sentence += 1  # return

            for id__ in dic_source_relationships:
                destination_xml_id = dic_source_relationships[id__][0]

                for des in destination_xml_id.split(","):
                    dict_coordinates = get_hash(id__)
                    if des in linked_entity_registry:
                        span_destination = linked_entity_registry[des]
                        span_source = linked_entity_registry[dict_coordinates]

                        relations_sentence.append(
                            [span_destination[0], span_destination[1], span_source[0], span_source[1],
                             get_relationship_name(span_source[2], span_destination[2])])

        if len(str.strip("".join(tokens_paragraph))) > 0:
            paragraphs.append(tokens_paragraph)
            ner.append(ner_sentence)
            relations.append(relations_sentence)
            i += 1

    return paragraphs, ner, relations


def process_sentences(children: list) -> [List, List, List]:
    """Process XML with <p> and <s> as sentences. Return a flat list of sentences."""
    token_offset_sentence = 0
    ient = 1

    # list containing text and the dictionary with all the annotations
    sentences = []
    ner = []
    relations = []

    i = 0
    for paragraph in children:
        for sentence in paragraph:
            j = 0
            text_sentence = ''
            tokens_sentence = []
            ner_sentence = []
            relations_sentence = []
            dic_dest_relationships = {}
            dic_source_relationships = {}
            linked_entity_registry = {}

            for item in sentence.contents:
                if type(item) == NavigableString:
                    local_text = str(item)
                    text_sentence += local_text

                    token_list = tokenise(item.string)
                    if len(token_list) > 0 and token_list[0] == ' ':  # remove space after tags
                        del token_list[0]

                    tokens_sentence.extend(token_list)
                    token_offset_sentence += len(token_list)

                elif type(item) is Tag and item.name == 'rs':
                    local_text = item.text
                    text_sentence += local_text
                    if 'type' not in item.attrs:
                        raise Exception("RS without type is invalid. Stopping")
                    label = item.attrs['type']
                    token_list = tokenise(local_text)
                    tokens_sentence.extend(token_list)

                    ner_entity = [token_offset_sentence, token_offset_sentence + len(token_list) - 1, label]
                    ner_sentence.append(ner_entity)

                    if len(item.attrs) > 0:
                        ## multiple entities can point ot the same one, so "corresp" value can be duplicated
                        allow_duplicates = False
                        span_id = None
                        if 'xml:id' in item.attrs:
                            span_id = item['xml:id']
                            if item.attrs['xml:id'] not in dic_dest_relationships:
                                dic_dest_relationships[item.attrs['xml:id']] = [i + 1, j + 1, ient, label]

                        if 'corresp' in item.attrs:
                            if span_id is None or span_id == "":
                                id_str = str(i + 1) + "," + str(j + 1)
                                span_id = get_hash(id_str)
                                if span_id not in dic_source_relationships:
                                    dic_source_relationships[span_id] = [item.attrs['corresp'].replace('#', ''),
                                                                         ient,
                                                                         label]
                            else:
                                if span_id not in dic_source_relationships:
                                    dic_source_relationships[span_id] = [item.attrs['corresp'].replace('#', ''),
                                                                         ient,
                                                                         label]

                            allow_duplicates = True

                        if span_id is not None:
                            if span_id not in linked_entity_registry.keys():
                                linked_entity_registry[span_id] = ner_entity
                            else:
                                if not allow_duplicates:
                                    print("The same key exists... something's wrong: ", span_id)

                    token_offset_sentence += len(token_list)

                    j += 1

                # elif use_paragraphs and type(item) is Tag and item.name == 's':
                #
                #     local_text = str(item)
                #     text_sentence += local_text

                ient += 1  # entity No.

            # token_offset_sentence += 1  # return

            sentences.append(tokens_sentence)
            ner.append(ner_sentence)
            i += 1

            for id__ in dic_source_relationships:
                destination_xml_id = dic_source_relationships[id__][0]

                for des in destination_xml_id.split(","):
                    dict_coordinates = get_hash(id__)
                    if des in linked_entity_registry:
                        span_destination = linked_entity_registry[des]
                        span_source = linked_entity_registry[dict_coordinates]

                        relations_sentence.append(
                            [span_destination[0], span_destination[1], span_source[0], span_source[1],
                             get_relationship_name(span_source[2], span_destination[2])])

            relations.append(relations_sentence)

    return sentences, ner, relations


def get_sentences_nodes(soup, grouped=True) -> Union[List, List[List]]:
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

    data_grouped = [tags_title] + [[z for z in y.find_all(sentence_tag)] for y in tags_text + tags_captions]

    if not grouped:
        data_flattened = [sentence for paragraph in data_grouped for sentence in paragraph]
        return data_flattened

    return data_grouped


def get_paragraphs_nodes(soup) -> Union[List, List[List]]:
    tags_title = []
    tags_text = []
    tags_captions = []

    paragraph_tag = "p"

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

    data = tags_title + [y for y in tags_text + tags_captions]

    return data


def get_children_list_grouped(soup, use_paragraphs=False) -> Union[List, List[List]]:
    tags_title = []
    tags_text = []
    tags_captions = []

    paragraph_tag = "p"
    sentence_tag = "s"

    for child in soup.tei.children:
        if child.name == 'teiHeader':
            # [y for x in list(filter(lambda c: c.name in ['teiHeader', 'text'], soup.tei.children)) for y in filter(lambda o: type(o) == Tag,  x.children)]
            tags_title.extend([paragraph for paragraph in child.find_all("title")])
            tags_text.extend([paragraph for subchildren in child.find_all("abstract") for paragraph in
                              subchildren.find_all(paragraph_tag)])
            tags_text.extend([paragraph for paragraph in child.find_all("ab", {"type": "keywords"})])

        elif child.name == 'text':
            tags_text.extend([paragraph for subchildren in child.find_all("body") for paragraph in
                              subchildren.find_all(paragraph_tag)])
            tags_captions.extend([paragraph for paragraph in child.find_all("ab")])

    data_grouped = [tags_title] + [[z for z in y.find_all(sentence_tag)] for y in tags_text + tags_captions]

    if use_paragraphs:
        data_grouped = [[sentence for sentence in paragraph] for paragraph in data_grouped]

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
