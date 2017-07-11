import sys
import os
import re
import urllib2
import ssl
from makeCourse import HACKMD_URL

def downloadFile(url,loc):
	ctx = ssl.create_default_context()
	ctx.check_hostname = False
	ctx.verify_mode = ssl.CERT_NONE
	u = urllib2.urlopen(url, context=ctx)
	f = open(loc, 'wb')
	meta = u.info()
	file_size_dl = 0
	block_sz = 8192
	while True:
		buffer = u.read(block_sz)
		if not buffer:
			break
		file_size_dl += len(buffer)
		f.write(buffer)
	f.close()

def download(url):
	ctx = ssl.create_default_context()
	ctx.check_hostname = False
	ctx.verify_mode = ssl.CERT_NONE
	req = urllib2.Request(url, context=ctx)
	response = urllib2.urlopen(req, context=ctx)
	return response.read()

def getHackmdDocument(course_config,code):
	url = HACKMD_URL+'/'+code+'/download'
	if course_config['args'].verbose:
		print '    Getting document from hackMD: %s'%url
	mdContents = download(url)
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
			downloadFile(url,outPath)
			mdContents = mdContents.replace(m.group(1),course_config['web_dir']+"static/"+outFile)
	return mdContents

def getSlidesPDF(course_config,slidesCode):
	url = HACKMD_URL+'/'+slidesCode+'/pdf'
	if course_config['args'].verbose:
		print '    Getting document from hackMD: %s'%url

	outFile = slidesCode+".pdf"
	outPath = os.path.join(course_config['build_dir'],'static',outFile)
	print '        %s=>%s'%(outFile,outPath)
	downloadFile(url,outPath)


