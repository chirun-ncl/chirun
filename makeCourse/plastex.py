import os
import re
from datetime import datetime
import glob
import sys
import pkg_resources
import shutil
from distutils.dir_util import copy_tree
from subprocess import Popen, PIPE 
from jinja2 import Template
from makeCourse import *

def fixPlastexQuirks(text):
	#This takes something like $ stuff $ and turns it into $stuff$.
	#Mathjax doesn't allow whitespace just after opening $ or just before closing $.
	reInlineEqn = re.compile(r'(^|[^\$])\$([^\$]+?)\$(?=[^\$]|$)')
	text = reInlineEqn.sub(lambda m: m.group(1)+' $'+m.group(2).strip()+'$', text)

	#Stop markdown from listifying things.
	reItemList = re.compile(r'<p>\s*([\(\[]*)([A-z0-9]{1,3})([\)\]\.\:])')
	text = reItemList.sub(lambda m: '<p>'+m.group(1)+m.group(2)+"\\"+m.group(3), text)
	return text

def runPlastex(course_config,inFile,tmpDir):
	outPath = os.path.join(course_config['args'].dir,tmpDir)
	inPath = os.path.join(course_config['args'].dir,inFile)

	cmd = 'plastex --dir=%s --sec-num-depth=3 --split-level=-1 --toc-non-files --renderer=HTML5ncl %s 2>&1'%(outPath,inPath)

	if course_config['args'].verbose:
		print 'Running plastex: %s'%cmd
	proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	for line in iter(proc.stdout.readline, ''):
		if course_config['args'].veryverbose:
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
	#Markdown Images
	mdImage = re.compile(r'!\[[^\]]*\]\(([^\)]*)\)')
	for m in re.finditer(mdImage, texContents):
		inFile = os.path.basename(m.group(1))
		inPath = os.path.join(course_config['args'].dir,tmpDir,'images',inFile)
		outPath = os.path.join(course_config['build_dir'],'static',title,inFile)
		outDir  = os.path.join(course_config['build_dir'],'static',title)
		if course_config['args'].verbose:
			print '        %s=> %s'%(inPath,outPath)
		#ACTUALLY MOVE THE FILE
		mkdir_p(outDir)
		shutil.copyfile(inPath.strip(), outPath.strip())
		texContents = texContents.replace(m.group(1),os.path.join(course_config['build_dir'],'static',title, inFile))

	#Tikz Images
	tikzImage = re.compile(r'<object class=\"tikzpicture\" data=\"([^\)]*)\" type=\"image/svg\+xml\">')
	for m in re.finditer(tikzImage, texContents):
		inFile = os.path.basename(m.group(1))
		inPath = os.path.join(course_config['args'].dir,tmpDir,'images',inFile)
		outPath = os.path.join(course_config['build_dir'],'static',title,inFile)
		outDir  = os.path.join(course_config['build_dir'],'static',title)
		if course_config['args'].verbose:
			print '        %s=> %s'%(inPath,outPath)
		#ACTUALLY MOVE THE FILE
		mkdir_p(outDir)
		shutil.copyfile(inPath.strip(), outPath.strip())
		texContents = texContents.replace(m.group(1),os.path.join(course_config['build_dir'],'static',title, inFile))

	return texContents
	