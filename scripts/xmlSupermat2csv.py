import argparse
import csv
import os
import re
from pathlib import Path

from bs4 import BeautifulSoup, Tag

from supermat.supermat_tei_parser import get_children_list

def write_on_file(fw, filename, sentenceText, dic_token):
    links = len([token for token in dic_token if token[5] != '_'])
    has_links = 0 if links == 0 else 1
    fw.writerow([filename, sentenceText, has_links])


def processFile(finput):
    with open(finput, encoding='utf-8') as fp:
        doc = fp.read()

    mod_tags = re.finditer(r'(</\w+>) ', doc)
    for mod in mod_tags:
        doc = doc.replace(mod.group(), ' ' + mod.group(1))
    #     print(doc)
    soup = BeautifulSoup(doc, 'xml')

    children = get_children_list(soup)

    dic_dest_relationships = {}
    dic_source_relationships = {}
    ient = 1
    i = 0
    for child in children:
        for pTag in child:
            j = 0
            for item in pTag.contents:
                if type(item) is Tag:
                    if 'type' not in item.attrs:
                        raise Exception("RS without type is invalid. Stopping")
                    entity_class = item.attrs['type']
                    entity_text = item.text

                    if len(item.attrs) > 0:
                        if 'xml:id' in item.attrs:
                            if item.attrs['xml:id'] not in dic_dest_relationships:
                                dic_dest_relationships[item.attrs['xml:id']] = [i + 1, j + 1, ient, entity_text,
                                                                                entity_class]

                        if 'corresp' in item.attrs:
                            if (i + 1, j + 1) not in dic_source_relationships:
                                dic_source_relationships[i + 1, j + 1] = [item.attrs['corresp'].replace('#', ''), ient,
                                                                          entity_text, entity_class]
                    j += 1
                ient += 1
            i += 1

    output = []
    output_idx = []

    struct = {
        'id': None,
        'material': None,
        'tcValue': None,
        'pressure': None,
        'me_method': None
    }
    mapping = {}

    for label in list(struct.keys()):
        if label not in mapping:
            mapping[label] = {}

        for par_num, token_num in dic_source_relationships:
            source_entity_id = dic_source_relationships[par_num, token_num][1]
            source_id = str(par_num) + '-' + str(token_num)
            source_text = dic_source_relationships[par_num, token_num][2]
            source_label = dic_source_relationships[par_num, token_num][3]

            # destination_xml_id: Use this to pick up information from dic_dest_relationship
            destination_xml_id = dic_source_relationships[par_num, token_num][0]

            for des in destination_xml_id.split(","):
                destination_item = dic_dest_relationships[str(des)]

                destination_id = destination_item[2]
                destination_text = destination_item[3]
                destination_label = destination_item[4]
                if destination_label != label:
                    continue

                try:
                    relationship_name = get_relationship_name(source_label, destination_label)
                except Exception as e:
                    return []

                if source_label not in mapping:
                    mapping[source_label] = {}

                if destination_id in mapping[destination_label]:
                    indexes_in_output_table = mapping[destination_label][destination_id]
                    for index_in_output_table in indexes_in_output_table:
                        if source_label in output[index_in_output_table]:
                            row_copy = {key: value for key, value in output[index_in_output_table].items()}
                            row_copy[destination_label] = destination_text
                            row_copy[source_label] = source_text
                            output.append(row_copy)
                            # output.append({destination_label: destination_text, source_label: source_text})
                        else:
                            output[index_in_output_table][source_label] = source_text
                elif source_entity_id in mapping[source_label]:
                    indexes_in_output_table = mapping[source_label][source_entity_id]
                    for index_in_output_table in indexes_in_output_table:
                        if destination_label in output[index_in_output_table]:
                            # output.append({destination_label: destination_text, source_label: source_text})
                            # if source_label in output[index_in_output_table]:
                            #     output.append({destination_label: destination_text, source_label: source_text})
                            # else:
                            row_copy = {key: value for key, value in output[index_in_output_table].items()}
                            row_copy[source_label] = source_text
                            row_copy[destination_label] = destination_text
                            output.append(row_copy)
                        else:
                            output[index_in_output_table][destination_label] = destination_text
                else:
                    output.append({destination_label: destination_text, source_label: source_text})
                    output_idx.append({destination_label: destination_id, source_label: source_id})

                current_index = len(output) - 1
                if destination_id not in mapping[destination_label]:
                    mapping[destination_label][destination_id] = set()
                    mapping[destination_label][destination_id].add(current_index)
                else:
                    mapping[destination_label][destination_id].add(current_index)

                if source_entity_id not in mapping[source_label]:
                    mapping[source_label][source_entity_id] = set()
                    mapping[source_label][source_entity_id].add(current_index)
                else:
                    mapping[source_label][source_entity_id].add(current_index)

    return output


def get_relationship_name(source_label, destination_label):
    relationship_name = ""
    if str.lower(source_label) == 'tcvalue':
        if destination_label == 'material':
            relationship_name = 'tcValue-material'
        elif destination_label == 'me_method':
            relationship_name = 'me_method-tcValue'
        else:
            raise Exception("Something is wrong in the links. "
                            "The link between " + source_label + " and " + destination_label + " is invalid. ")
    elif str.lower(source_label) == 'pressure':
        if str.lower(destination_label) == 'tcvalue':
            relationship_name = 'tcValue-pressure'
    else:
        raise Exception("Something is wrong in the links. "
                        "The link between " + source_label + " and " + destination_label + " is invalid. ")

    return relationship_name


def writeOutput(data, output_path, format):
    delimiter = '\t' if format == 'tsv' else ','
    fw = csv.writer(open(output_path, encoding='utf-8', mode='w'), delimiter=delimiter, quotechar='"')
    columns = ['id', 'material', 'tcValue', 'pressure', 'me_method', 'filename']
    fw.writerow(columns)
    for d in data:
        fw.writerow([d[c] if c in d else '' for c in columns])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Converter XML (Supermat) to a tabular values (CSV, TSV)")

    parser.add_argument("--input", help="Input file or directory", required=True)
    parser.add_argument("--output", help="Output directory", required=True)
    parser.add_argument("--recursive", action="store_true", default=False,
                        help="Process input directory recursively. If input is a file, this parameter is ignored.")
    parser.add_argument("--format", default='csv', choices=['tsv', 'csv'],
                        help="Output format.")
    parser.add_argument("--filter", default='all', choices=['all', 'oa', 'non-oa'],
                        help='Extract data from a certain type of licenced documents')

    args = parser.parse_args()

    input = args.input
    output = args.output
    recursive = args.recursive
    format = args.format
    filter = args.filter

    if os.path.isdir(input):
        path_list = []

        if recursive:
            for root, dirs, files in os.walk(input):
                for file_ in files:
                    if not file_.lower().endswith(".xml"):
                        continue

                    if filter == 'oa':
                        if '-CC' not in file_:
                            continue
                    elif filter == 'non-oa':
                        if '-CC' in file_:
                            continue

                    abs_path = os.path.join(root, file_)
                    path_list.append(abs_path)

        else:
            path_list = Path(input).glob('*.xml')

        data = []
        for path in path_list:
            print("Processing: ", path)
            file_data = processFile(path)
            for r in file_data:
                r['filename'] = Path(path).name
            data.extend(file_data)

        if os.path.isdir(str(output)):
            output_path = os.path.join(output, "output") + "." + format
        else:
            parent_dir = Path(output).parent
            output_path = os.path.join(parent_dir, "output." + format)

        writeOutput(data, output_path, format)

    elif os.path.isfile(input):
        input_path = Path(input)
        data = processFile(input_path)
        output_filename = input_path.stem

        writeOutput(data, os.path.join(output, str(output_filename) + "." + format), format)
