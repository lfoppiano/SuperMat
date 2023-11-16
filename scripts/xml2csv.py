import argparse
import csv
import os
import sys
from collections import OrderedDict
from pathlib import Path
from typing import List

from src.supermat.supermat_tei_parser import process_file_to_json
from src.supermat.utils import get_in_paths_from_directory


def process_file(finput, use_paragraphs=False):
    json = process_file_to_json(finput, use_paragraphs=use_paragraphs)

    data_list = []
    spans_map = OrderedDict()
    spans_links_map = OrderedDict()
    spans_links_reverse_map = OrderedDict()

    filename = Path(finput).name
    passages = json['passages']
    for passage_id, passage in enumerate(passages):
        passage_common_parts = {
            'id': passage_id,
            'filename': filename,
            'passage_id': str(passage['group_id']) + "|" + str(passage['id']) if 'group_id' in passage else str(
                passage['id']),
            'text': passage['text']
        }
        passage['passage_id'] = passage_common_parts['passage_id']

        spans_passage_map, spans_passage_links_map, spans_passage_links_reverse_map = get_span_maps(passage)
        spans_map.update(spans_passage_map)
        spans_links_map.update(spans_passage_links_map)
        spans_links_reverse_map.update(spans_passage_links_reverse_map)

        spans_by_type = OrderedDict()
        for t in ['tcValue', 'material', 'pressure', 'me_method']:
            spans_by_type[t] = {key: submap for key, submap in spans_passage_map.items() if 'type' in submap and submap['type'] == t}

        records_in_passage = []
        for span_id, span in spans_by_type['tcValue'].items():
            # for span_id, span in spans_by_type[t].items():

            outbound = spans_links_map[span_id] if span_id in spans_links_map.keys() else []
            inbound = spans_links_reverse_map[span_id] if span_id in spans_links_reverse_map.keys() else []

            # if passage['id'] == 17:
            #     print(inbound)

            for out in sorted(list(set(outbound + inbound))):
                if out in spans_map:
                    span_out = spans_map[out]
                    records_to_update = list(filter(
                        lambda rip: span['type'] in rip and span_id == rip[span['type']][0] and span_out['type'] not in rip,
                        records_in_passage))

                    if len(records_to_update) == 0:
                        records_in_passage.append({'tcValue': (span_id, spans_map[span_id]['text']), span_out['type']: (span_out['id'], span_out['text'])})
                    else:
                        for record_to_update in records_to_update:
                            record_to_update[span_out['type']] = (span_out['id'], span_out['text'])

        for re in records_in_passage:
            ids = [re[key][0] for key in re.keys()]
            is_same_passage = all(id_value in spans_passage_map.keys() for id_value in ids)
            for key, value in passage_common_parts.items():
                if not is_same_passage:
                    if key != "text":
                        re[key] = value
                else:
                    re[key] = value

        data_list.extend(records_in_passage)

    spans_by_type = {}
    ## Recover possible items not tcValue, that were not linked before
    for ent_type in ['material', 'pressure', 'me_method']:
        spans_by_type[ent_type] = {key: submap for key, submap in spans_map.items() if 'type' in submap and submap['type'] == ent_type}
        for span_id, span in spans_by_type[ent_type].items():
            outbound = spans_links_map[span_id] if span_id in spans_links_map.keys() else []
            inbound = spans_links_reverse_map[span_id] if span_id in spans_links_reverse_map.keys() else []

            for out in list(set(outbound + inbound)):
                if out in spans_map:
                    span_out = spans_map[out]
                    records_to_update = list(filter(lambda rip: span['type'] not in rip and span_out['type'] in rip and span_out['id'] ==
                                    rip[span_out['type']][0], data_list))

                    if len(records_to_update) > 0:
                        for record_to_update in records_to_update:
                            record_to_update[span['type']] = (span['id'], span['text'])
                            if span['passage_id'] != record_to_update['passage_id']:
                                record_to_update['text'] = ""

    for re in data_list:
        for column in re.keys():
            if column not in ['id', 'filename', 'passage_id', 'text']:
                re[column] = re[column][1]

    return data_list


def get_span_maps(passage):
    span_links_map = OrderedDict()
    span_links_reverse_map = OrderedDict()
    span_map = OrderedDict()

    for span in passage['spans']:
        if 'id' in span:
            if span['id'] not in span_map:
                span_map[span['id']] = span
                span['passage_id'] = passage['passage_id']
                if 'links' in span:
                    for link in span['links']:
                        target_id = link['targetId']
                        source_id = span['id']
                        if target_id not in span_links_map:
                            span_links_map[target_id] = [source_id]
                        else:
                            span_links_map[target_id].append(source_id)

                        if source_id not in span_links_reverse_map:
                            span_links_reverse_map[source_id] = [target_id]
                        else:
                            span_links_reverse_map[source_id].append(target_id)
            else:
                print("error")

    return span_map, span_links_map, span_links_reverse_map


def write_output(output_path: List, data: List[dict], columns: List):
    with open(output_path, encoding='utf-8', mode='w') as fo:
        fw = csv.writer(fo, delimiter=",", quotechar='"')
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
        path_list = get_in_paths_from_directory(input, ".xml", recursive=recursive)

        output_data = []
        for path in path_list:
            print("Processing: ", path)
            file_output_data = process_file(path, use_paragraphs=use_paragraphs)
            # data = sorted(file_data, key=lambda k: k['passage_id'])
            output_data.extend(file_output_data)

        if os.path.isdir(str(output)):
            output_path = os.path.join(output, "output") + "." + format
        else:
            parent_dir = Path(output).parent
            output_path = os.path.join(parent_dir, "output." + format)

    elif os.path.isfile(input):
        input_path = Path(input)
        output_data = process_file(input_path, use_paragraphs=use_paragraphs)
        # data_sorted = sorted(data, key=lambda k: k['paragraph_id'])
        output_filename = input_path.stem
        output_path = os.path.join(output, str(output_filename) + "." + format)
    else:
        print("The input should be either a file or a directory")
        sys.exit(-1)

    data = [{**record, **{"id": idx}} for idx, record in enumerate(output_data)]

    columns = ['id', 'filename', 'passage_id', 'material', 'tcValue', 'pressure', 'me_method', 'text']
    write_output(output_path, data, columns)
