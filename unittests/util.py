import typing

def parse_css_attribute(style: str) -> typing.Dict[str,str]:
    """ 
        Very basic 'parsing' of the contents of an HTML element's ``style`` attribute (a single block of CSS).
        Splits by ``;`` characters, and then by ``:``, to get a dictionary mapping rules to values.
    """

    return {k.strip():v.strip() for k,v in [x.split(':') for x in style.split(';')]}
