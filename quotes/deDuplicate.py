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
from util import clean_text


def de_duplicate(files, output):
    """
    Input a list of JL files, output a single processed JL file
    """
    items = {}
    punct_regex = re.compile('[%s]' % re.escape(string.punctuation))

    for pth in files:
        with open(pth, 'rb') as fd:
            for item in json_lines.reader(fd):
                # Fix and normalize text
                item['text'] = clean_text(item['text'])
                # Lower and strip punctuation
                txt = punct_regex.sub('', item['text'].lower())
                # Drop extra spaces
                txt = ' '.join(txt.split())
                if txt in items:
                    # Merge existing tags
                    item['tags'].extend(items[txt]['tags'])
                    item['tags'] = sorted(set(t.lower() for t in item['tags']))
                else:
                    # Normalize tags
                    item['tags'] = sorted(t.lower() for t in item['tags'])
                # The dict KEY will automatically overwrite duplicates
                items[txt] = item

    out_items = sorted(items.values(), key=lambda x: x['author'].lower())
    print(f'Written {len(out_items)} items in "{output}".')
    json.dump(out_items, open(output, 'w'))


if __name__ == '__main__':
    de_duplicate(['brainyQuotes.jl', 'quoteWorld.jl'], 'unifiedQuotes.json')
