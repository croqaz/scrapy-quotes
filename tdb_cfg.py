#
# Text-DB config file
#
# export('~/Dev/scrapy-quotes/notebooks/exported_quotes.jl')
#


def keys(o):
    return o['text'].lower().replace(' ', '')


def validate(o):
    return isinstance(o, dict) \
        and len(o) > 1 and len(o) < 5 \
        and len(o.get('text', '')) > 3


tdb_config = {'keys': keys, 'validate': validate}
