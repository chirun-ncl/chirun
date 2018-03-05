import logging
import os
import re
import ssl
import sys
import urllib2
from makeCourse import HACKMD_URL

logger = logging.getLogger(__name__)

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
	req = urllib2.Request(url)
	response = urllib2.urlopen(req, context=ctx)
	return response.read()

def getHackmdDocument(course_config,code):
	url = HACKMD_URL+'/'+code+'/download'
	logger.info('    Getting document from hackMD: {}'.format(url))
	mdContents = download(url)
	return mdContents

def getEmbeddedImages(course_config,mdContents):
	logger.info('    Downloading embedded images:')
	mdImage = re.compile(r'!\[[^\]]*\]\(([^\)]*)\)')
	for m in re.finditer(mdImage, mdContents):
		if course_config['args'].verbose:
			url = m.group(1)
			if 'http' not in url:
				url = HACKMD_URL + m.group(1)
			outFile = os.path.basename(m.group(1))
			outPath = os.path.join(course_config['build_dir'],'static',outFile)
			logger.debug('        {file}=>{path}'.format(file=outFile,path=outPath))
			downloadFile(url,outPath)
			mdContents = mdContents.replace(m.group(1),os.path.join(course_config['build_dir'],'static',outFile))
	return mdContents

def getSlidesPDF(course_config,slidesCode):
	url = HACKMD_URL+'/'+slidesCode+'/pdf'
	logger.info('    Getting document from hackMD: {}'.format(url))

	outFile = slidesCode+".pdf"
	outPath = os.path.join(course_config['build_dir'],'static',outFile)
	logger.debug('        {file}=>{path}'.format(file=outFile,path=outPath))
	downloadFile(url,outPath)
