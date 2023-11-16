import os
from pathlib import Path
from typing import List


def get_in_paths_from_directory(input_path: str, input_file_extension: str, recursive: bool = True) -> List:
    path_list = []

    if recursive:
        for root, dirs, files in os.walk(input_path):
            for file_ in files:
                if not file_.lower().endswith(input_file_extension):
                    continue

                abs_path = os.path.join(root, file_)
                path_list.append(abs_path)

    else:
        path_list = Path(input_path).glob("*.{}".format(input_file_extension))

    return path_list


def get_in_out_paths_from_directory(
        input: str,
        output: str,
        input_file_extension: str,
        output_file_extension: str,
        recursive=True
) -> List:
    path_list = []
    if recursive:
        for root, dirs, files in os.walk(input):
            for dir in dirs:
                abs_path_dir = os.path.join(root, dir)
                output_path = abs_path_dir.replace(str(input.rstrip("/")), str(output))
                os.makedirs(output_path, exist_ok=True)

            for file_ in files:
                if not file_.lower().endswith(input_file_extension):
                    continue

                file_input_path = os.path.join(root, file_)
                output_path = file_input_path.replace(str(input.rstrip("/")), str(output))
                file_output_path = output_path.replace(input_file_extension, output_file_extension).replace(".tei", "")
                path_list.append([file_input_path, file_output_path])

    else:
        input_path_list = list(Path(input).glob("*{}".format(input_file_extension)))
        output_path_list = [str(input_path)
                            .replace(str(input), str(output))
                            .replace(input_file_extension, output_file_extension)
                            .replace(".tei", "") for input_path
                            in input_path_list]

        path_list = list(zip(input_path_list, output_path_list))

    return path_list
