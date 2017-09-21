import re
import sys
import os
import errno
import yaml

HACKMD_URL = "https://mas-coursebuild.ncl.ac.uk"

def slugify(value):
	return "".join([c for c in re.sub(r'\s+','_',value) if c.isalpha() or c.isdigit() or c=='_']).rstrip().lower()

def temp_path(path):
	tmp_dir = 'tmp'
	if not os.path.exists(tmp_dir):
		os.makedirs(tmp_dir)
	return os.path.join(tmp_dir,'{}-{}'.format(os.urandom(2).encode('hex'),path))

def isHidden(obj):
	if 'hidden' in obj.keys():
		if obj['hidden']:
			return True
	return False

def containsMockTest(obj):
	mocktest = filter(lambda item: item['type'] == 'mocktest', obj['structure'])
	if mocktest:
		return True
	return False

def getMockTest(obj):
	mocktest = filter(lambda item: item['type'] == 'mocktest', obj['structure'])
	if mocktest:
		return mocktest[0]['source']
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
