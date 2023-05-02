from pymdownx.superfences import fence_code_format
from bs4 import BeautifulSoup
import uuid


def codemirror_formatter(source, language, css_class, options, md):
    """Formatter for codemirror blocks."""
    if 'lang' in options:
        language = options['lang'].lower()

    html = fence_code_format(source, language, 'cm-block', options, md)
    soup = BeautifulSoup(html, features="lxml")
    pretag = soup.find("pre")

    if language == 'matlab':
        pretag["data-language"] = 'octave'
    else:
        pretag["data-language"] = language

    pretag['data-uuid'] = str(uuid.uuid4())
    return pretag


def editable_formatter(source, language, css_class, options, md):
    pretag = codemirror_formatter(source, language, css_class, options, md)
    return str(pretag)


def runnable_formatter(source, language, css_class, options, md):
    code_language = options.get('lang').lower()
    return f'''<runnable-code language="{code_language}" class="{css_class}">{source}</runnable-code>'''

def output_formatter(source, language, css_class, options, md):
    if 'class' in options:
        cls = options['class']
    else:
        cls = 'output-block'
    html = fence_code_format(source, language, cls, options, md)
    return html


def runnable_validator(language, options):
    """Options validator for runnable codemirror code blocks."""
    okay = True
    if 'lang' not in options:
        okay = False
    return okay


def editable_validator(language, options):
    """Options validator for codemirror code blocks."""
    okay = True
    return okay


def output_validator(language, options):
    """Options validator for codemirror code blocks."""
    okay = True
    return okay
