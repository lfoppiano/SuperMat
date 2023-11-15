import argparse
import json
import os
from pathlib import Path

from supermat.supermat_tei_parser import process_file_to_json

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
