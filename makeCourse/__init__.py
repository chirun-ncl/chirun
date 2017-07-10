import re
import sys
import os
import errno

HACKMD_URL = "http://makara.ncl.ac.uk:8080"

def slugify(value):
	return "".join([c for c in re.sub(r'\s+','_',value) if c.isalpha() or c.isdigit() or c=='_']).rstrip().lower()

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
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise