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

	cmd = ['pdflatex','-halt-on-error', item.in_file]
	logger.info('Running pdflatex: {}'.format(os.path.join(inDir,item.in_file)))

	#latex often requires 2 runs to resolve labels
	for _ in range(2):
		proc = Popen(cmd, stdout=PIPE, stderr=PIPE, cwd=inDir, universal_newlines=True)
		for stdout_line in iter(proc.stdout.readline, ""):
			logger.debug(stdout_line)

		out, err = proc.communicate()
		
		if proc.returncode != 0:
			logger.error(err)
			raise Exception("Error: Something went wrong running pdflatex!")

	outPath = os.path.join(course.config['build_dir'],item.out_file+".pdf")
	logger.info('    Moving pdf output: {file} => {path}'.format(file=os.path.join(inDir,item.base_file+'.pdf'),path=outPath))
	shutil.move(os.path.join(inDir,item.base_file+'.pdf'), outPath)

	if not course.args.lazy:
		logger.info('    Cleaning up after pdflatex...')
		extensions = ['.log','.aux','.out','.pdf','.snm','.nav','.toc']
		for extension in extensions:
			filename = '{base}{extension}'.format(base=os.path.join(inDir,item.base_file), extension=extension)
			logger.info('        Deleting: {}'.format(filename))
			try:
				os.remove(filename)
			except OSError:
				pass

if __name__ == "__main__":
	pass
