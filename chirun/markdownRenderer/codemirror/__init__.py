from pymdownx.superfences import fence_code_format


def runnable_formatter(source, language, css_class, options, md, **kwargs):
    code_language = options.get('lang').lower()
    return f'''<runnable-code language="{code_language}" class="{css_class}">{source}</runnable-code>'''


def runnable_validator(language, inputs, options, attrs, md):
    """Options validator for runnable codemirror code blocks."""
    if 'lang' not in inputs:
        return False
    options['lang'] = inputs['lang']
    return True


def output_formatter(source, language, css_class, options, md, **kwargs):
    if 'class' in options:
        cls = options['class']
    else:
        cls = 'output-block'
    html = fence_code_format(source, language, cls, options, md, **kwargs)
    return html


def output_validator(language, inputs, options, attrs, md):
    """Options validator for codemirror code blocks."""
    for k,v in inputs:
        options[k] = v
    return True
