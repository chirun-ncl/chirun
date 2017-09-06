import logging
import os
import pkg_resources
import re
import sys
from subprocess import Popen, PIPE 

logger = logging.getLogger(__name__)

def runPdflatex(course_config,ch,inFile,inDir=None):
	if not inDir:
		inDir = course_config['args'].dir
	baseFile = re.sub(r'.tex$','',inFile)

	cmd = ['pdflatex',inFile,'&&','pdflatex',inFile]
	logger('Running pdflatex: {}'.format(os.path.join(inDir,inFile)))
	proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, cwd=inDir)
	out, err = proc.communicate()
	logger.debug(out)
	if proc.returncode != 0:
		sys.stderr.write("Error: Something went wrong running pdflatex! Quitting...\n")
		if not course.config['args'].veryverbose:
			sys.stderr.write("(Use -vv for more information)\n")
		sys.exit(2)

	outPath = os.path.join(course_config['build_dir'],ch['outFile']+".pdf")
	logger.info('    Copying pdf output: %s => %s'%(os.path.join(inDir,baseFile+'.pdf'),outPath))
	cmd = 'cp %s %s'%(os.path.join(inDir,baseFile+'.pdf'),outPath)
	proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	if course_config['args'].veryverbose:
		logger.debug('    %s'%cmd )
		logger.debug(proc.stdout.read())
		proc.stdout.close()
	rc = proc.wait()
	if rc != 0:
		sys.stderr.write("Error: Something went wrong copying resulting pdf! Quitting...\n")
		sys.stderr.write("(Use -vv for more information)\n")
		sys.exit(2)


	logging.info('    Cleaning up after pdflatex...')
	logging.info('        Deleting: %s.log'%os.path.join(course_config['args'].dir,baseFile))
	logging.info('        Deleting: %s.aux'%os.path.join(course_config['args'].dir,baseFile))
	logging.info('        Deleting: %s.out'%os.path.join(course_config['args'].dir,baseFile))
	logging.info('        Deleting: %s.pdf'%os.path.join(course_config['args'].dir,baseFile))
	logging.info('        Deleting: %s.snm'%os.path.join(course_config['args'].dir,baseFile))
	logging.info('        Deleting: %s.nav'%os.path.join(course_config['args'].dir,baseFile))
	logging.info('        Deleting: %s.toc'%os.path.join(course_config['args'].dir,baseFile))

	try:
		os.remove('%s.aux'%os.path.join(course_config['args'].dir,baseFile))
	except OSError:
		pass
	try:
		os.remove('%s.log'%os.path.join(course_config['args'].dir,baseFile))
	except OSError:
		pass
	try:
		os.remove('%s.out'%os.path.join(course_config['args'].dir,baseFile))
	except OSError:
		pass
	try:
		os.remove('%s.pdf'%os.path.join(course_config['args'].dir,baseFile))
	except OSError:
		pass
	try:
		os.remove('%s.snm'%os.path.join(course_config['args'].dir,baseFile))
	except OSError:
		pass
	try:
		os.remove('%s.nav'%os.path.join(course_config['args'].dir,baseFile))
	except OSError:
		pass
	try:
		os.remove('%s.toc'%os.path.join(course_config['args'].dir,baseFile))
	except OSError:
		pass

if __name__ == "__main__":
	pass
