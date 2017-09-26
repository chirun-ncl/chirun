import logging
import os
import pkg_resources
import re
import shutil
import sys
from subprocess import Popen, PIPE 

logger = logging.getLogger(__name__)

def runPdflatex(course,item):
	inDir = os.path.join(course.root_dir,os.path.dirname(item.source))
	inFile = os.path.basename(item.source)

	baseFile, _ = os.path.splitext(inFile)

	cmd = ['pdflatex','-halt-on-error', inFile]
	logger.info('Running pdflatex: {}'.format(os.path.join(inDir,inFile)))

	#latex often requires 2 runs to resolve labels
	for _ in range(2):
		proc = Popen(cmd, stdout=PIPE, stderr=PIPE, cwd=inDir)
		out, err = proc.communicate()
		logger.debug(out)
		if proc.returncode != 0:
			logger.error(err)
			raise Exception("Error: Something went wrong running pdflatex!")

	outPath = os.path.join(course.config['build_dir'],item.out_file+".pdf")
	logger.info('    Copying pdf output: {file} => {path}'.format(file=os.path.join(inDir,baseFile+'.pdf'),path=outPath))
	shutil.copyfile(os.path.join(inDir,baseFile+'.pdf'), outPath)

	logger.info('    Cleaning up after pdflatex...')
	extensions = ['.log','.aux','.out','.pdf','.snm','.nav','.toc']
	for extension in extensions:
		filename = '{base}{extension}'.format(base=os.path.join(inDir,baseFile), extension=extension)
		logger.info('        Deleting: {}'.format(filename))
		try:
			os.remove(filename)
		except OSError:
			pass

if __name__ == "__main__":
	pass
