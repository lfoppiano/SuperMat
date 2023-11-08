import regex as re

# Generic simple tokenizer for Indo-European languages
# also python side of GROBID default tokenizer, used for Indo-European languages
# Source: http://github.com/kermitt2/delft


delimiters = "\n\r\t\f\u00A0([ ^%‰°•⋅·,:;?.!/)-–−‐=≈~∼<>+\"“”‘’'`#$]*\u2666\u2665\u2663\u2660\u00A0"

regex = '|'.join(map(re.escape, delimiters))
regex_second_step = "(?<=[a-zA-Z])(?=\\d)|(?<=\\d)(?=\\D)"

# additional parenthesis are for capturing delimiters and keep then in the token list
pattern = re.compile('(' + regex + '|' + regex_second_step + ')')
# pattern = re.compile('(' + regex + ')')

blanks = ' \t\n'


def tokenizeSimple(text):
    tokens, offsets = tokenize(text)

    return tokens


def tokenize(text):
    """
    Tokenization following the above pattern with offset information
    """
    offset = 0
    offsets = []
    tokens = []
    for index, match in enumerate(pattern.split(text)):
        if len(match) == 0:
            continue
        tokens.append(match)
        position = (offset, offset + len(match))
        offsets.append(position)
        offset = offset + len(match)

    return tokens, offsets


def tokenizeAndFilter(text):
    """
    Tokenization following the above pattern with offset information
    """
    tokens, offsets = tokenize(text)

    finalTokens = []
    finalOffsets = []
    i = 0
    for token in tokens:
        if token not in blanks:
            finalTokens.append(token)
            finalOffsets.append(offsets[i])
        i += 1
    return finalTokens, finalOffsets


def tokenizeAndFilterSimple(text):
    """
    Tokenization following the above pattern without offset information
    """
    tokens = []
    for index, match in enumerate(pattern.split(text)):
        if len(match) == 0:
            continue

        tokens.append(match)

    finalTokens = []
    i = 0
    for token in tokens:
        if token not in blanks:
            finalTokens.append(token)
        i += 1

    return finalTokens


def filterSpace(token):
    return (token not in blanks)


if __name__ == "__main__":
    # some tests
    test = 'this is a test, but a stupid test!!'
    print(test)
    print(tokenizeAndFilterSimple(test))
    print(tokenizeAndFilter(test))

    test = '\nthis is yet \u2666 another, dummy... test,\na [stupid] test?!'
    print(test)
    print(tokenizeAndFilterSimple(test))
    print(tokenizeAndFilter(test))
