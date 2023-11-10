import argparse
import csv
import os
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Tag

from supermat.supermat_tei_parser import get_children_list_grouped

from src.supermat.supermat_tei_parser import get_sentences_nodes

paragraph_id = 'paragraph_id'


def process_file(finput, use_paragraphs=False):
    filename = Path(finput).name.split(".superconductors")[0]
    with open(finput, encoding='utf-8') as fp:
        doc = fp.read()

    # mod_tags = re.finditer(r'(</\w+>) ', doc)
    # for mod in mod_tags:
    #     doc = doc.replace(mod.group(), ' ' + mod.group(1))
    #     print(doc)
    soup = BeautifulSoup(doc, 'xml')

    paragraphs_grouped = get_sentences_nodes(soup, grouped=True)

    dic_dest_relationships = {}
    dic_source_relationships = {}
    ient = 1
    i = 0
    for para_id, paragraph in enumerate(paragraphs_grouped):
        for sent_id, sentence in enumerate(paragraph):
            j = 0
            for item in sentence.contents:
                if type(item) is Tag:
                    if 'type' not in item.attrs:
                        raise Exception("RS without type is invalid. Stopping")
                    entity_class = item.attrs['type']
                    entity_text = item.text

                    if len(item.attrs) > 0:
                        if 'xml:id' in item.attrs:
                            if item.attrs['xml:id'] not in dic_dest_relationships:
                                dic_dest_relationships[item.attrs['xml:id']] = [i + 1, j + 1, ient, entity_text,
                                                                                entity_class, para_id, sent_id]

                        if 'corresp' in item.attrs:
                            if (i + 1, j + 1) not in dic_source_relationships:
                                dic_source_relationships[i + 1, j + 1] = [item.attrs['corresp'].replace('#', ''), ient,
                                                                          entity_text, entity_class, para_id, sent_id]
                    j += 1
                ient += 1
            i += 1

    output = []
    output_idx = []

    struct = {
        'id': None,
        'filename': None,
        'paragraph_id': None,
        'material': None,
        'tcValue': None,
        'pressure': None,
        'me_method': None,
        'sentence': None
    }
    mapping = {}

    for label in list(struct.keys()):
        if label not in mapping:
            mapping[label] = {}

        for par_num, token_num in dic_source_relationships:
            source_item = dic_source_relationships[par_num, token_num]
            source_entity_id = source_item[1]
            source_id = str(par_num) + '-' + str(token_num)
            source_text = source_item[2]
            source_label = source_item[3]

            # destination_xml_id: Use this to pick up information from dic_dest_relationship
            destination_xml_id = source_item[0]

            for des in destination_xml_id.split(","):
                destination_item = dic_dest_relationships[str(des)]

                destination_id = destination_item[2]
                destination_text = destination_item[3]
                destination_label = destination_item[4]
                destination_para = destination_item[5]
                destination_sent = destination_item[6]
                if destination_label != label:
                    continue

                # try:
                #     relationship_name = get_relationship_name(source_label, destination_label)
                # except Exception as e:
                #     return []

                if source_label not in mapping:
                    mapping[source_label] = {}

                if destination_id in mapping[destination_label]:
                    indexes_in_output_table = mapping[destination_label][destination_id]
                    for index_in_output_table in indexes_in_output_table:
                        if source_label in output[index_in_output_table]:
                            row_copy = {key: value for key, value in output[index_in_output_table].items()}
                            row_copy[destination_label] = destination_text
                            row_copy[source_label] = source_text
                            row_copy['filename'] = filename
                            row_copy["paragraph_id"] = destination_para
                            row_copy["sentence_id"] = destination_sent
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
                            row_copy['filename'] = filename
                            row_copy["paragraph_id"] = destination_para
                            row_copy["sentence_id"] = destination_sent
                            output.append(row_copy)
                        else:
                            output[index_in_output_table][destination_label] = destination_text
                else:
                    output.append(
                        {
                            destination_label: destination_text,
                            source_label: source_text,
                            'filename': filename,
                            paragraph_id: destination_para,
                            "sentence_id": destination_sent
                        }
                    )
                    output_idx.append(
                        {
                            destination_label: destination_id,
                            source_label: source_id,
                            'filename': filename,
                            paragraph_id: destination_para,
                            "sentence_id": destination_sent
                        }
                    )

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


def write_output(data, output_path, format, use_paragraphs=False):
    # passage_id_column_name = 'paragraph_id' if use_paragraphs else 'sentence_id'
    delimiter = '\t' if format == 'tsv' else ','
    fw = csv.writer(open(output_path, encoding='utf-8', mode='w'), delimiter=delimiter, quotechar='"')
    columns = ['id', 'filename', 'paragraph_id', 'sentence_id', 'material', 'tcValue', 'pressure', 'me_method']
    fw.writerow(columns)
    for d in data:
        fw.writerow([d[c] if c in d else '' for c in columns])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Converter XML (Supermat) to a tabular values (CSV, TSV)")

    parser.add_argument("--input",
                        help="Input file or directory",
                        required=True)
    parser.add_argument("--output",
                        help="Output directory",
                        required=True)
    parser.add_argument("--recursive",
                        action="store_true",
                        default=False,
                        help="Process input directory recursively. If input is a file, this parameter is ignored.")
    parser.add_argument("--format",
                        default='csv',
                        choices=['tsv', 'csv'],
                        help="Output format.")
    parser.add_argument("--use-paragraphs",
                        default=False,
                        action="store_true",
                        help="Uses paragraphs instead of sentences")

    args = parser.parse_args()

    input = args.input
    output = args.output
    recursive = args.recursive
    format = args.format
    use_paragraphs = args.use_paragraphs

    if os.path.isdir(input):
        path_list = []

        if recursive:
            for root, dirs, files in os.walk(input):
                for file_ in files:
                    if not file_.lower().endswith(".xml"):
                        continue

                    abs_path = os.path.join(root, file_)
                    path_list.append(abs_path)

        else:
            path_list = Path(input).glob('*.xml')

        data_sorted = []
        for path in path_list:
            print("Processing: ", path)
            file_data = process_file(path, use_paragraphs=use_paragraphs)
            data = sorted(file_data, key=lambda k: k[paragraph_id])
            data_sorted.extend(data)

        if os.path.isdir(str(output)):
            output_path = os.path.join(output, "output") + "." + format
        else:
            parent_dir = Path(output).parent
            output_path = os.path.join(parent_dir, "output." + format)

    elif os.path.isfile(input):
        input_path = Path(input)
        data = process_file(input_path, use_paragraphs=use_paragraphs)
        data_sorted = sorted(data, key=lambda k: k[paragraph_id])
        output_filename = input_path.stem
        output_path = os.path.join(output, str(output_filename) + "." + format)
    else:
        print("The input should be either a file or a directory")
        sys.exit(-1)

    data = [{**record, **{"id": idx}} for idx, record in enumerate(data_sorted)]

    write_output(data, output_path, format)
