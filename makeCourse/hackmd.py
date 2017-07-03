import sys
import os
import re
import urllib2
from makeCourse import HACKMD_URL


def downloadImage(url,loc):
	u = urllib2.urlopen(url)
	f = open(loc, 'wb')
	meta = u.info()
	file_size = int(meta.getheaders("Content-Length")[0])
	print "Downloading: %s of size %s bytes..." % (loc, file_size)

	file_size_dl = 0
	block_sz = 8192
	while True:
		buffer = u.read(block_sz)
		if not buffer:
			break
		file_size_dl += len(buffer)
		f.write(buffer)
	f.close()

def downloadMD(url):
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	return response.read()

def getHackmdDocument(course_config,code):
	url = HACKMD_URL+'/'+code+'/download'
	if course_config['args'].verbose:
		print '    Getting document from hackMD: %s'%url
	mdContents = downloadMD(url)
	return mdContents

def getEmbeddedImages(course_config,mdContents):
	if course_config['args'].verbose:
		print '    Downloading embedded images:'
	mdImage = re.compile(r'!\[[^\]]*\]\(([^\)]*)\)')
	for m in re.finditer(mdImage, mdContents):
		if course_config['args'].verbose:
			url = m.group(1)
			if 'http' not in url:
				url = HACKMD_URL + m.group(1)
			outFile = os.path.basename(m.group(1))
			outPath = os.path.join(course_config['build_dir'],'static',outFile)
			print '        %s=>%s'%(outFile,outPath)
			downloadImage(url,outPath)
			mdContents = mdContents.replace(m.group(1),"/static/"+outFile)
	return mdContents


