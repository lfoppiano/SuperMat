import argparse
import json
import os
import re
from collections import OrderedDict
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag
from supermat.grobid_tokenizer import tokenizeSimple
from supermat.supermat_tei_parser import get_children_list, get_section, get_hash


def tokenise(string):
    return tokenizeSimple(string)


def write_on_file(fw, paragraphText, dic_token, i, item_length):
    # tsvText += f'#Text={paragraphText}\n'
    print(f'#Text={paragraphText}', file=fw)
    for k, v in dic_token.items():
        # print(v)
        if k[0] == i + 1 and v[2]:
            print('{}-{}\t{}-{}\t{}\t{}\t{}\t{}\t{}\t{}\t'.format(*k, *v), file=fw)

    # Avoid adding a line break too much at the end of the file
    if i != item_length - 1:
        print('', file=fw)


def process_file(finput, use_paragraphs=False):
    with open(finput, encoding='utf-8') as fp:
        doc = fp.read()

    mod_tags = re.finditer(r'(</\w+>) ', doc)
    for mod in mod_tags:
        doc = doc.replace(mod.group(), ' ' + mod.group(1))
    soup = BeautifulSoup(doc, 'xml')

    children = get_children_list(soup, use_paragraphs=use_paragraphs)

    off_token = 0
    ient = 1

    # list containing text and the dictionary with all the annotations
    paragraphs = []
    dic_dest_relationships = {}
    dic_source_relationships = {}

    output_document = OrderedDict()
    output_document['lang'] = 'en'
    output_document['level'] = 'sentence' if not use_paragraphs else 'paragraph'
    output_document['paragraphs'] = paragraphs

    linked_entity_registry = {}

    i = 0
    for child in children:
        for pTag in child:
            paragraph = OrderedDict()
            j = 0
            offset = 0
            section = get_section(pTag)
            if not section:
                section = get_section(pTag.parent)

            paragraph['section'] = section
            paragraph_text = ''
            paragraph['text'] = paragraph_text
            spans = []
            paragraph['spans'] = spans
            tokens = []
            paragraph['tokens'] = tokens
            for item in pTag.contents:
                if type(item) == NavigableString:
                    local_text = str(item)
                    paragraph_text += local_text
                    offset += len(local_text)

                elif type(item) is Tag and item.name == 'rs':
                    local_text = item.text
                    paragraph_text += local_text

                    span = OrderedDict()
                    front_offset = 0
                    if local_text.startswith(" "):
                        front_offset = len(local_text) - len(local_text.lstrip(" "))

                    span['text'] = local_text.strip(" ")
                    span['offset_start'] = offset + front_offset
                    span['offset_end'] = offset + len(span['text']) + front_offset
                    spans.append(span)

                    offset += len(local_text)

                    assert paragraph_text[span['offset_start']:span['offset_end']] == span['text']

                    if 'type' not in item.attrs:
                        raise Exception("RS without type is invalid. Stopping")

                    entity_class = item.attrs['type']
                    span['type'] = '<' + entity_class + '>'

                    if len(item.attrs) > 0:
                        ## multiple entities can point ot the same one, so "corresp" value can be duplicated
                        allow_duplicates = False
                        if 'xml:id' in item.attrs:
                            span['id'] = item['xml:id']
                            if item.attrs['xml:id'] not in dic_dest_relationships:
                                dic_dest_relationships[item.attrs['xml:id']] = [i + 1, j + 1, ient, entity_class]

                        if 'corresp' in item.attrs:
                            if 'id' not in span or span['id'] == "":
                                id_str = str(i + 1) + "," + str(j + 1)
                                span['id'] = get_hash(id_str)
                                if (span['id']) not in dic_source_relationships:
                                    dic_source_relationships[span['id']] = [item.attrs['corresp'].replace('#', ''),
                                                                            ient,
                                                                            entity_class]
                            else:
                                if (span['id']) not in dic_source_relationships:
                                    dic_source_relationships[span['id']] = [item.attrs['corresp'].replace('#', ''),
                                                                            ient,
                                                                            entity_class]

                            allow_duplicates = True

                        if 'id' in span:
                            if span['id'] not in linked_entity_registry.keys():
                                linked_entity_registry[span['id']] = span
                            else:
                                if not allow_duplicates:
                                    print("The same key exists... something's wrong: ", span['id'])

                    j += 1

                ient += 1  # entity No.

            paragraph['text'] = paragraph_text
            off_token += 1  # return

            paragraphs.append(paragraph)
            i += 1

    for id__ in dic_source_relationships:
        destination_xml_id = dic_source_relationships[id__][0]
        # source_entity_id = dic_source_relationships[par_num, token_num][1]
        # label_source = dic_source_relationships[id__][2]

        # destination_xml_id: Use this to pick up information from dic_dest_relationship

        for des in destination_xml_id.split(","):
            destination_item = dic_dest_relationships[str(des)]
            # destination_paragraph_tsv = destination_item[0]
            # destination_token_tsv = destination_item[1]
            # destination_entity_id = destination_item[2]
            # label_destination = destination_item[3]

            # relationship_name = get_relationship_name(label, destination_label)

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

            if 'links' in span_source:
                span_source['links'].append(link_source)
            else:
                span_source['links'] = [link_source]

            if 'links' in span_destination:
                span_destination['links'].append(link_destination)
            else:
                span_destination['links'] = [link_destination]

    return output_document


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Converter from XML (Grobid training data based on TEI) to lossy JSON (CORD-19) format")

    parser.add_argument("--input",
                        help="Input file or directory",
                        required=True)
    parser.add_argument("--output",
                        required=True,
                        help="Output directory")
    parser.add_argument("--recursive",
                        action="store_true",
                        default=False,
                        help="Process input directory recursively. If input is a file, this parameter is ignored. ")
    parser.add_argument("--use-paragraphs",
                        action="store_true",
                        default=False,
                        help="Use paragraphs instead of sentences.")

    args = parser.parse_args()

    input = args.input
    output = args.output
    recursive = args.recursive
    use_paragraphs = args.use_paragraphs

    if os.path.isdir(input):
        path_list = []
        output_path_list = []

        if recursive:
            for root, dirs, files in os.walk(input):
                for dir in dirs:
                    abs_path_dir = os.path.join(root, dir)
                    output_path = abs_path_dir.replace(str(input.rstrip("/")), str(output))
                    os.makedirs(output_path, exist_ok=True)

                for file_ in files:
                    if not file_.lower().endswith(".tei.xml"):
                        continue

                    file_input_path = os.path.join(root, file_)
                    output_path = file_input_path.replace(str(input.rstrip("/")), str(output))
                    file_output_path = output_path.replace(".xml", ".json").replace(".tei", "")
                    path_list.append([file_input_path, file_output_path])

        else:
            input_path_list = list(Path(input).glob('*.tei.xml'))
            output_path_list = [str(input_path)
                           .replace(str(input), str(output))
                           .replace(".xml", ".json")
                           .replace(".tei", "") for input_path
                           in input_path_list]

            path_list = list(zip(input_path_list, output_path_list))

        for file_input_path, file_output_path  in path_list:
            print("Processing: ", file_input_path)

            output_document = process_file(str(file_input_path), use_paragraphs)
            with open(file_output_path, 'w') as fp:
                json.dump(output_document, fp)

    elif os.path.isfile(input):
        input_path = Path(input)
        output_filename = os.path.join(output, input_path.stem + ".json")
        output_document = process_file(input_path, use_paragraphs)
        with open(output_filename, 'w') as fp:
            json.dump(output_document, fp)
