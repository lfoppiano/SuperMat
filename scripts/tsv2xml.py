import argparse
import os
from html import escape
from pathlib import Path

from bs4 import BeautifulSoup


def processFile(file):
    output = {'paragraphs': [], 'rel_source_dest': [], 'rel_dest_source': []}

    spans = []
    tokens = []

    currentParagraph = {'text': "", 'spans': spans, 'tokens': tokens, 'section': 'body'}

    inside = False

    with open(file) as fp:
        tokenPreviousPositionEnd = '-1'
        previousTagIndex = None
        previousTagValue = None
        tagIndex = None
        tagValue = None
        currentSpan = None
        tokenId = 0
        entitiesLayerFirstIndex = -1
        sectionLayerFirstIndex = -1
        hasDocumentStructure = False


        # If there are no relationships, the TSV has two column less.
        with_relationships = False
        relation_source_dest = {}
        relation_dest_source = {}
        spans_layers = 3
        relationship_layer_index = 5  # The usual value
        for line in fp.readlines():
            if line.startswith("#Text") and not inside:  # Start paragraph
                currentParagraph['text'] = line.replace("#Text=", "")
                inside = True
                tokenId = 0

            elif not line.strip() and inside:  # End paragraph
                if currentSpan:
                    spans.append(currentSpan)

                output['paragraphs'].append(currentParagraph)
                currentParagraph = {'text': "", 'spans': [], 'tokens': [], 'section': "body"}

                spans = currentParagraph['spans']
                tokens = currentParagraph['tokens']
                tokenPreviousPositionEnd = '-1'
                previousTagIndex = None
                previousTagValue = None
                tagIndex = None
                tagValue = None
                currentSpan = None

                inside = False
            else:
                if not inside:
                    if line.startswith("#T_SP"):
                        layerName = line.split('|')[0].split('=')[1]
                        if layerName == 'webanno.custom.Supercon':
                            entitiesLayerFirstIndex = spans_layers
                            entitiesLayerLabelIndex = entitiesLayerFirstIndex + 1
                        elif layerName == 'webanno.custom.Section':
                            sectionLayerFirstIndex = spans_layers
                            hasDocumentStructure = True
                        layerTagsets = len(line.split('|')) - 1
                        spans_layers += layerTagsets

                    if line.startswith("#T_RL"):
                        with_relationships = True
                        if spans_layers > 0:
                            relationship_layer_index = entitiesLayerLabelIndex + 1

                    print("Ignoring " + line)
                    continue

                split = line.split('\t')
                annotationId = split[0]
                position = split[1]
                tokenPositionStart = position.split("-")[0]
                tokenPositionEnd = position.split("-")[1]

                if tokenPreviousPositionEnd != tokenPositionStart and tokenPreviousPositionEnd != '-1':  ## Add space in the middle #fingercrossed
                    tokens.append(
                        {'start': tokenPreviousPositionEnd, 'end': tokenPositionStart, 'text': " ", 'id': tokenId})
                    tokenId = tokenId + 1

                text = split[2]
                tokens.append({'start': tokenPositionStart, 'end': tokenPositionEnd, 'text': text, 'id': tokenId})

                section = "body"
                if sectionLayerFirstIndex > -1:
                    section = split[3].split('[')[0]

                currentParagraph['section'] = section
                tag = split[entitiesLayerLabelIndex].strip()
                tag = tag.replace('\\', '')

                if with_relationships:
                    relationship_name = split[relationship_layer_index].strip()
                    relationship_references = split[relationship_layer_index + 1].strip()
                else:
                    relationship_name = '_'
                    relationship_references = '_'

                relationships = []  # list of tuple(source, destination)

                if relationship_name != '_' and relationship_references != '_':
                    # We ignore the name of the relationship for the moment
                    # names = relationship_name.split("|")

                    # We split by | as they are grouped as
                    # 2-162	1965-1969	YBCO	*[1]	material[1]	material-tc|material-tc	2-176[0_1]|2-179[0_1]
                    references = relationship_references.split("|")
                    for reference in references:
                        reference_split = reference.split('[')
                        if len(reference_split) == 1:
                            # no disambiguation ids, so I use
                            #   destination = layer-token (element 0)
                            #   source = layer-token of reference (elemnt 6)

                            source = reference
                            destination = annotationId
                        elif len(reference_split) > 1:
                            reference_source_tsv = reference_split[0]
                            source = reference_split[1].split('_')[0]
                            destination = reference_split[1].split('_')[1][:-1]

                            if source == '0':
                                source = reference_source_tsv
                            elif destination == '0':
                                destination = annotationId

                        relationships.append((source, destination))
                        if source not in relation_source_dest:
                            relation_source_dest[source] = [destination]
                        else:
                            relation_source_dest[source].append(destination)

                        if destination not in relation_dest_source:
                            relation_dest_source[destination] = [source]
                        else:
                            relation_dest_source[destination].append(source)

                if tag != '_' and not tag.startswith('*'):
                    if tag.endswith("]"):
                        tagValue = tag.split('[')[0]
                        tagIndex = tag.split('[')[1][:-1]
                    else:
                        tagValue = tag
                        tagIndex = -1

                    if tagIndex != -1:
                        if tagIndex != previousTagIndex:
                            if currentSpan:
                                spans.append(currentSpan)
                            currentSpan = {'start': tokenPositionStart, 'end': tokenPositionEnd, 'token_start': tokenId,
                                           'token_end': tokenId, 'label': tagValue, 'tagIndex': tagIndex,
                                           'relationships': relationships}
                        else:
                            if tagValue == previousTagValue:
                                currentSpan['end'] = tokenPositionEnd
                                currentSpan['token_end'] = tokenId
                            else:
                                if currentSpan:
                                    spans.append(currentSpan)
                                currentSpan = {'start': tokenPositionStart, 'end': tokenPositionEnd,
                                               'token_start': tokenId,
                                               'token_end': tokenId, 'label': tagValue, 'tagIndex': tagIndex,
                                               'relationships': relationships}
                    else:
                        if currentSpan:
                            spans.append(currentSpan)
                        currentSpan = {'start': tokenPositionStart, 'end': tokenPositionEnd, 'token_start': tokenId,
                                       'token_end': tokenId, 'label': tagValue, 'tagIndex': annotationId,
                                       'relationships': relationships}

                else:
                    if currentSpan:
                        spans.append(currentSpan)
                        currentSpan = None

                tokenId = tokenId + 1

                tokenPreviousPositionEnd = tokenPositionEnd  # copy the position end
                previousTagIndex = tagIndex  # index of the tag in the tsv
                previousTagValue = tagValue

        # print(output)
        # if not line.startswith(str(paragraph_index) + "-"):
        #     print("Something is wrong in the synchronisation " + str(paragraph_index) + " vs " + line[0:4])
        #     sys.exit(-255)

        # print(split)

    output['paragraphs'].append(currentParagraph)
    output['rel_dest_source'] = relation_dest_source
    output['rel_source_dest'] = relation_source_dest
    return output


xmlTemplate = """<tei xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc xml:id="_0">
            <titleStmt/>
            <publicationStmt>
                <publisher>National Institute for Materials Science (NIMS), Tsukuba, Japan</publisher>
                <availability>
                    <licence target="http://creativecommons.org/licenses/by/3.0/">
                        <p>The Creative Commons Attribution 3.0 Unported (CC BY 3.0) Licence applies to this document.</p>
                    </licence>
                </availability>
            </publicationStmt>
        </fileDesc>
        <encodingDesc>
            <appInfo>
                <application version="project.version" ident="grobid-superconductors">
                    <ref target="https://github.com/lfoppiano/grobid-superconductors">A machine learning software for extracting materials and their properties from scientific literature.</ref>
                </application>
            </appInfo>
        </encodingDesc>
        <profileDesc>
            <abstract/>            
        </profileDesc>
    </teiHeader>
    <text xml:lang="en">
        <body/>
    </text>
</tei>"""


def get_text_under_body(soup):
    children = soup.findChildren('text')
    return children[0] if children is not None and len(
        children) > 0 else None


def writeOutput(datas, output):
    paragraphs = []
    rel_dest_source = datas['rel_dest_source']
    rel_source_dest = datas['rel_source_dest']
    for data in datas['paragraphs']:
        tokens = data['tokens']
        spans = data['spans']
        text = data['text']
        section = data['section']
        paragraph = ''

        spanIdx = 0

        for i, token in enumerate(tokens):
            if spanIdx < len(spans):
                span = spans[spanIdx]
                span_token_start = span['token_start']
                span_token_end = span['token_end']
                span_label = span['label']
            else:
                span = None

            if span is not None:
                if i < span_token_start:
                    paragraph += escape(token['text'])
                    continue
                    # paragraph += token['text']
                elif span_token_start <= i <= span_token_end:
                    if i == span_token_start:
                        tagLabel = '<rs type="' + span_label + '">'
                        pointers = ''
                        identifier = ''
                        if span['tagIndex'] in rel_source_dest:
                            first = True
                            for dest in rel_source_dest[span['tagIndex']]:
                                if first:
                                    first = False
                                    pointers = ' corresp="#x' + dest
                                else:
                                    pointers += ',#x' + dest
                            pointers += '"'

                        if span['tagIndex'] in rel_dest_source:
                            identifier = ' xml:id="x' + span['tagIndex'] + '"'

                        if pointers != '' or identifier != '':
                            tagLabel = '<rs type="' + span_label + '"' + identifier + pointers + '>'

                        paragraph += tagLabel
                    paragraph += escape(token['text'])
                    if i == span_token_end:
                        # paragraph += token['text']
                        paragraph += '</rs>'
                        spanIdx += 1

            else:
                paragraph += escape(token['text'])

        paragraphs.append((section, paragraph))

    with open(output, 'w') as fo:
        soup = BeautifulSoup(xmlTemplate, 'xml')
        for section, paragraphObj in paragraphs:
            if section == 'title':
                tag = BeautifulSoup('<title>' + paragraphObj + '</title>', 'xml')
                soup.teiHeader.titleStmt.append(tag)
            elif section == 'abstract':
                tag = BeautifulSoup('<p>' + paragraphObj + '</p>', 'xml')
                soup.teiHeader.profileDesc.abstract.append(tag)
            elif section == 'keywords':
                tag = BeautifulSoup('<ab type="keywords">' + paragraphObj + '</ab>', 'xml')
                soup.teiHeader.profileDesc.append(tag)
            elif section == 'body':
                tag = BeautifulSoup('<p>' + paragraphObj + '</p>', 'xml')
                text_tag = get_text_under_body(soup)
                text_tag.body.append(tag)
            elif section == 'figureCaption' or section == 'tableCaption':
                tag = BeautifulSoup('<ab type="' + section + '">' + paragraphObj + '</ab>', 'xml')
                text_tag = get_text_under_body(soup)
                text_tag.body.append(tag)

        fo.write(str(soup))
        fo.flush()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Converter TSV to XML (Grobid training data based on TEI)")

    parser.add_argument("--input", help="Input file or directory", required=True)
    parser.add_argument("--output",
                        help="Output directory (if omitted, the output will be the same directory/file with different extension)",
                        required=False)
    parser.add_argument("--recursive", action="store_true", default=False,
                        help="Process input directory recursively. If input is a file, this parameter is ignored. ")

    args = parser.parse_args()

    input = args.input
    output = args.output
    recursive = args.recursive

    if os.path.isdir(input):
        path_list = []

        if recursive:
            for root, dirs, files in os.walk(input):
                for file_ in files:
                    if not file_.lower().endswith(".tsv"):
                        continue

                    abs_path = os.path.join(root, file_)
                    path_list.append(abs_path)

        else:
            path_list = Path(input).glob('*.tsv')

        for path in path_list:
            print("Processing: ", path)
            output_filename = Path(path).stem
            data = processFile(path)
            parent_dir = Path(path).parent
            if os.path.isdir(str(output)):
                output_path = os.path.join(output, str(output_filename)) + ".tei.xml"
            else:
                output_path = os.path.join(parent_dir, output_filename + ".tei.xml")

            writeOutput(data, output_path)

    elif os.path.isfile(input):
        input_path = Path(input)
        data = processFile(input_path)
        output_filename = input_path.stem
        writeOutput(data, os.path.join(output, str(output_filename) + ".tei.xml"))
