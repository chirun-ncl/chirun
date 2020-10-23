import re
import os
import yaml


def slugify(value):
    return "".join([c for c in re.sub(r'\s+', '_', value) if c.isalpha() or c.isdigit() or c == '_']).rstrip().lower()[:20]


def gen_dict_extract(key, var):
    """
        Yield every value corresponding to the given key at any level in the nested dictionary `var`
    """
    if hasattr(var, 'items'):
        for k, v in var.items():
            if k == key:
                yield var
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(key, d):
                        yield result


def mkdir_p(path):
    try:
        os.makedirs(str(path))
    except OSError:
        if not path.is_dir():
            raise


def yaml_header(data):
    return '---\n{}\n---\n\n'.format(yaml.dump(data, default_flow_style=False))
