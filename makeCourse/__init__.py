import re

HACKMD_URL = "http://makara.ncl.ac.uk:8080"

def slugify(value):
	return "".join([c for c in re.sub(r'\s+','_',value) if c.isalpha() or c.isdigit() or c=='_']).rstrip().lower()

def isHidden(obj):
	if 'hidden' in obj.keys():
		if obj['hidden']:
			return True
	return False