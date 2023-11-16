import argparse
import json
import os
from pathlib import Path

from supermat.supermat_tei_parser import process_file_to_json
from supermat.utils import get_in_out_paths_from_directory

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
        path_list = get_in_out_paths_from_directory(input, output, ".xml", ".json", recursive=recursive)

        for file_input_path, file_output_path in path_list:
            print("Processing: ", file_input_path)

            output_document = process_file_to_json(str(file_input_path))
            with open(file_output_path, 'w') as fp:
                json.dump(output_document, fp)

    elif os.path.isfile(input):
        input_path = Path(input)
        output_filename = os.path.join(output, input_path.stem + ".json")
        output_document = process_file_to_json(input_path)
        with open(output_filename, 'w') as fp:
            json.dump(output_document, fp)
