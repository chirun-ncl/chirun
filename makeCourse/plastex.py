import os
import re
from datetime import datetime
import glob
import sys
import pkg_resources
import shutil
from subprocess import Popen, PIPE 
from jinja2 import Template
from makeCourse import *

def fixPlastexQuirks(text):
	#This takes something like $ stuff $ and turns it into $stuff$.
	#Mathjax doesn't allow whitespace just after opening $ or just before closing $.
	reInlineEqn = re.compile(r'(^|[^\$])\$([^\$]+?)\$(?=[^\$]|$)')
	text = reInlineEqn.sub(lambda m: m.group(1)+' $'+m.group(2).strip()+'$', text)
	return text

def runPlastex(course_config,inFile,tmpDir):
	outPath = os.path.join(course_config['args'].dir,tmpDir)
	inPath = os.path.join(course_config['args'].dir,inFile)

	cmd = 'plastex --dir=%s --split-level=-1 --renderer=HTML5ncl %s'%(outPath,inPath)

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


def getEmbeddedImages(course_config,texContents,tmpDir,title):
	if course_config['args'].verbose:
		print '    Moving embedded images:'
	mdImage = re.compile(r'!\[[^\]]*\]\(([^\)]*)\)')
	for m in re.finditer(mdImage, texContents):
		if course_config['args'].verbose:
			inFile = os.path.basename(m.group(1))
			inPath = os.path.join(course_config['args'].dir,tmpDir,'images',inFile)
			outPath = os.path.join(course_config['build_dir'],'static',title,inFile)
			outDir  = os.path.join(course_config['build_dir'],'static',title)
			print '        %s=> %s'%(inPath,outPath)
			#ACTUALLY MOVE THE FILE
			mkdir_p(outDir)
			shutil.copyfile(inPath.strip(), outPath.strip())
			texContents = texContents.replace(m.group(1),os.path.join(course_config['build_dir'],'static',title, inFile))
	return texContents
	