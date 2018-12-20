
import re


def clean_text(text):
    # Fix quotes and 3 dots
    text = text.replace('‘', "'").replace('’', "'")\
        .replace('…', '...').replace('. . .', '...')
    # Fix more than 3 dots
    text = re.sub('\\.{3,99}', '...', text)
    # Fix more than 2 dashes
    text = re.sub('-{2,99}', '--', text)
    # Fix no space after comma
    text = re.sub(',([a-zA-Z])', ', \\g<1>', text)

    return text
