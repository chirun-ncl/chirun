import logging
import os
import pkg_resources
import re
import shutil
import sys
from subprocess import Popen, PIPE 

logger = logging.getLogger(__name__)

def runPdflatex(course_config,ch,inFile,inDir=None):
	if not inDir:
		inDir = course_config['args'].dir
	baseFile = re.sub(r'.tex$','',inFile)

	cmd = ['pdflatex','-halt-on-error', inFile]
	logger.info('Running pdflatex: {}'.format(os.path.join(inDir,inFile)))

	#latex often requires 2 runs to resolve labels
	for _ in range(2):
		proc = Popen(cmd, stdout=PIPE, stderr=PIPE, cwd=inDir)
		out, err = proc.communicate()
		logger.debug(out)

	if proc.returncode != 0:
		sys.stderr.write("Error: Something went wrong running pdflatex! Quitting...\n")
		if not course_config['args'].veryverbose:
			sys.stderr.write("(Use -vv for more information)\n")
		sys.exit(2)

	outPath = os.path.join(course_config['build_dir'],ch['outFile']+".pdf")
	logger.info('    Copying pdf output: %s => %s'%(os.path.join(inDir,baseFile+'.pdf'),outPath))
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
