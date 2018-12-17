"""
The purpose of this script is to read more JL (json lines) files and
to eliminate duplicate quotes from the files.
A Quote should be represented as: text, author, tags and optionally other info.
The text is normalized to lower-case, all punctuation is stripped and
then the quotes automatically duplicated.
"""

import re
import string
import json
import json_lines


def de_duplicate(files, output):
    """
    Input a list of JL files, output a single processed JL file
    """
    items = {}
    punct_regex = re.compile('[%s]' % re.escape(string.punctuation))

    for pth in files:
        with open(pth, 'rb') as fd:
            for item in json_lines.reader(fd):
                # Lower and strip punctuation
                txt = punct_regex.sub('', item['text'].lower())
                # Drop extra spaces
                txt = ' '.join(txt.split())
                # The dict KEY will automatically overwrite duplicates
                items[txt] = item

    out_items = sorted(items.values(), key=lambda x: x['author'].lower())
    json.dump(out_items, open(output, 'w'))


if __name__ == '__main__':
    de_duplicate(['quoteWorld.jl'], 'unifiedQuotes.json')
