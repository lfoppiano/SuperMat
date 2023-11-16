import argparse
import csv
import os
from pathlib import Path

from supermat.supermat_tei_parser import process_file_to_json

from src.supermat.utils import get_in_paths_from_directory

paragraph_id = 'paragraph_id'


def write_output(output_path, data, header, format="csv"):
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
        description="Converter XML (Supermat) to CSV for entity extraction (no relation information are used)")

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
    parser.add_argument("--entity-type",
                        default="material",
                        required=False,
                        help="Select which entity type to extract.")
    parser.add_argument("--use-paragraphs",
                        default=False,
                        action="store_true",
                        help="Uses paragraphs instead of sentences. "
                             "By default this script assumes that the XML is at sentence level.")

    args = parser.parse_args()

    input = args.input
    output = args.output
    recursive = args.recursive
    ent_type = args.entity_type
    use_paragraphs = args.use_paragraphs

    if os.path.isdir(input):
        path_list = get_in_paths_from_directory(input, ".xml", recursive=recursive)

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
            output_path_text = os.path.join(output, "output-text") + ".csv"
            output_path_expected = os.path.join(output, "output-" + ent_type) + ".csv"
        else:
            parent_dir = Path(output).parent
            output_path_text = os.path.join(parent_dir, "output-text" + ".csv")
            output_path_expected = os.path.join(parent_dir, "output-" + ent_type + ".csv")

        header = ["id", "filename", "pid", ent_type]

        for idx, data in enumerate(entities_data):
            data[0] = idx

        write_output(output_path_expected, entities_data, header)

        header = ["id", "filename", "pid", "text"]
        for idx, data in enumerate(texts_data):
            data[0] = idx
        write_output(output_path_text, texts_data, header)

    elif os.path.isfile(input):
        input_path = Path(input)
        file_data = process_file_to_json(input_path, use_paragraphs=use_paragraphs)
        output_filename = input_path.stem

        output_path_text = os.path.join(output, str(output_filename) + "-text" + ".csv")
        texts_data = get_texts(file_data)
        for idx, data in enumerate(texts_data):
            data[0] = idx

        header = ["id", "filename", "pid", "text"]
        write_output(output_path_text, texts_data, header)

        output_path_expected = os.path.join(output, str(output_filename) + "-" + ent_type + ".csv")
        ent_data_no_duplicates = get_entity_data(file_data, ent_type)
        for idx, data in enumerate(ent_data_no_duplicates):
            data[0] = idx

        header = ["id", "filename", "pid", ent_type]
        write_output(output_path_expected, ent_data_no_duplicates, header)
