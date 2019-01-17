import re
import sys
import os
import errno
import yaml

def slugify(value):
	return "".join([c for c in re.sub(r'\s+','_',value) if c.isalpha() or c.isdigit() or c=='_']).rstrip().lower()

def isHidden(obj):
	if 'hidden' in obj.keys():
		if obj['hidden']:
			return True
	return False

def gen_dict_extract(key, var):
    if hasattr(var,'iteritems'):
        for k, v in var.iteritems():
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
        os.makedirs(path)
    except OSError as exc:
        if not os.path.isdir(path):
            raise

def yaml_header(data):
    return '---\n{}\n---\n\n'.format(yaml.dump(data,default_flow_style=False))
