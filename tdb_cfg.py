#
# Text-DB config file
#
# export('~/Dev/scrapy-quotes/notebooks/exported_quotes.jl')
#

import re
import string

punct_regex = re.compile('[%s‘’“” \r\n\xa0]' % re.escape(string.punctuation))


def keys(o):
    return punct_regex.sub('', o['text'].lower())


def validate(o):
    # and o.get('source') \
    return isinstance(o, dict) \
        and len(o) > 2 and len(o) <= 5 \
        and len(o.get('author', '')) > 3 \
        and len(o.get('text', '')) > 3


def clean_text(text):
    text = text.strip().replace('…', '...').replace('. . .', '...').replace('\xa0', ' ')
    text = re.sub('[‐‑–‒—―]', '-', text)
    text = re.sub('[⅋﹠＆🙰🙱🙲🙳🙴🙵]', '&', text)
    text = re.sub('[´ʻˮ՚‘’“”′″‴Ꞌꞌ🙶🙷🙸]', "'", text)
    text = re.sub('[!¡ǃ‼❕❗❢❣ꜝꜞꜟ︕﹗！]', '!', text)
    text = re.sub('[?؟᥄⁇❓❔]', '?', text)
    # Fix more than 3 dots
    text = re.sub('\\.{3,99}', '...', text)
    # Fix more than 2 dashes
    text = re.sub('-{2,99}', '--', text)
    # Fix no space after comma
    text = re.sub(',([a-zA-Z])', ', \\g<1>', text)
    text = text.strip("'").strip()
    if text[-1] != '.':
        text += '.'
    return text

def transform(o):
    o['text'] = clean_text(o['text'])
    if o.get('tags'):
        o['tags'] = sorted(t.strip().lower() for t in o['tags'])
    return o


tdb_config = {'keys': keys, 'validate': validate, 'transform': transform}
