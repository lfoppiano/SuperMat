import argparse
import csv
import os
from pathlib import Path

from supermat.supermat_tei_parser import process_file_to_json

paragraph_id = 'paragraph_id'


def write_on_file(fw, filename, sentenceText, dic_token):
    links = len([token for token in dic_token if token[5] != '_'])
    has_links = 0 if links == 0 else 1
    fw.writerow([filename, sentenceText, has_links])


def write_output(data, output_path, format, header):
    delimiter = '\t' if format == 'tsv' else ','
    fw = csv.writer(open(output_path, encoding='utf-8', mode='w'), delimiter=delimiter, quotechar='"')
    fw.writerow(header)
    fw.writerows(data)


def get_entity_data(data_sorted, ent_type):
    ent_data = [[pid, data_sorted['doc_key'], pid, "".join(data_sorted['passages'][pid][entity[0]:entity[1]])] for
                pid in range(0, len(data_sorted['ner'])) for entity in
                filter(lambda e: e[2] == ent_type, data_sorted['ner'][pid])]

    # We remove the duplicates of the materials that falls in the same passage
    seen_values = set()
    ent_data_no_duplicates = [item for item in ent_data if
                              str(item[1]) + str(item[2]) + str(item[3]) not in seen_values and not seen_values.add(
                                  str(item[1]) + str(item[2]) + str(item[3]))]

    return ent_data_no_duplicates


def get_texts(data_sorted):
    text_data = [[idx, data_sorted['doc_key'], idx, "".join(data_sorted['passages'][idx])] for idx in
                 range(0, len(data_sorted['passages']))]

    return text_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Converter XML (Supermat) to a tabular values (CSV, TSV) for entity extraction (no relation information are used)")

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
                        help="Uses paragraphs instead of sentences. By default this script assumes that the XML is at sentence level.")

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

        entities_data = []
        texts_data = []
        ent_type = "material"
        for path in path_list:
            print("Processing: ", path)
            file_data = process_file_to_json(path, use_paragraphs=use_paragraphs)
            # data = sorted(file_data, key=lambda k: k[paragraph_id])
            entity_data = get_entity_data(file_data, ent_type)
            entities_data.extend(entity_data)

            text_data = get_texts(file_data)
            texts_data.extend(text_data)

        if os.path.isdir(str(output)):
            output_path_text = os.path.join(output, "output-text") + "." + format
            output_path_expected = os.path.join(output, "output-" + ent_type) + "." + format
        else:
            parent_dir = Path(output).parent
            output_path_text = os.path.join(parent_dir, "output-text" + "." + format)
            output_path_expected = os.path.join(parent_dir, "output-" + ent_type + "." + format)

        header = ["id", "filename", "pid", ent_type]

        for idx, data in enumerate(entities_data):
            data[0] = idx

        write_output(entities_data, output_path_expected, format, header)

        header = ["id", "filename", "pid", "text"]
        for idx, data in enumerate(texts_data):
            data[0] = idx
        write_output(texts_data, output_path_text, format, header)

    elif os.path.isfile(input):
        input_path = Path(input)
        file_data = process_file_to_json(input_path, use_paragraphs=use_paragraphs)
        output_filename = input_path.stem

        output_path_text = os.path.join(output, str(output_filename) + "-text" + "." + format)
        texts_data = get_texts(file_data)
        for idx, data in enumerate(texts_data):
            data[0] = idx

        header = ["id", "filename", "pid", "text"]
        write_output(texts_data, output_path_text, format, header)

        ent_type = "material"
        output_path_expected = os.path.join(output, str(output_filename) + "-" + ent_type + "." + format)
        ent_data_no_duplicates = get_entity_data(file_data, ent_type)
        for idx, data in enumerate(ent_data_no_duplicates):
            data[0] = idx

        header = ["id", "filename", "pid", ent_type]
        write_output(ent_data_no_duplicates, output_path_expected, format, header)
