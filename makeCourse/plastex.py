import os
from datetime import datetime
import glob
import sys
import pkg_resources
import shutil
from subprocess import Popen, PIPE 
from jinja2 import Template

def runPlastex(course_config,inFile,tmpDir):
	outPath = os.path.join(course_config['args'].dir,tmpDir)
	inPath = os.path.join(course_config['args'].dir,inFile)

	cmd = 'plastex --dir=%s --split-level=-1 --renderer=HTML5ncl --dollars %s'%(outPath,inPath)

	if course_config['args'].verbose:
		print 'Running plastex: %s'%cmd
	proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	if course_config['args'].veryverbose:
		for line in iter(proc.stderr.readline, ''):
			print line
		proc.stdout.close()
	rc = proc.wait()
	if rc != 0:
		sys.stderr.write("Error: Something went wrong with the latex compilation! Quitting...\n")
		sys.stderr.write("(Use -vv for more information)\n")
		sys.exit(2)
	elif course_config['args'].verbose:
		print 'Done!'