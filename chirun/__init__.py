from plasTeX.Packages.embed import *  # noqa: F401, F403
from plasTeX.Packages.hyperref import *  # noqa: F401, F403
import re
import os
import yaml
import shutil


# Workaround for copytree on Python < 3.8
# https://stackoverflow.com/a/12514470
def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def slugify(value, v=0):
    slug = re.sub(r'[\W_]+','_', value).lower()[:20]

    if(v > 0):
        suffix = f'_{v}'
        slug = slug[:-len(suffix)]
        if slug.endswith('_'):
            slug = slug[:-1]
        slug = slug + suffix

    return slug


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
