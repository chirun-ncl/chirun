import glob
import logging
import os
import pkg_resources
import re
import shutil
import sys
from datetime import datetime
from distutils.dir_util import copy_tree
from jinja2 import Template
from makeCourse import *
from subprocess import Popen, PIPE 

logger = logging.getLogger(__name__)

class PlastexRunner:

	tmpDir = ''

	def load_latex_content(self,sourceItem):
		self.tmpDir = self.temp_path('plastex')
		self.runPlastex(sourceItem.source)
		texContents = open(os.path.join(self.root_dir,self.tmpDir, "index.html"), 'r').read()
		texContents = self.fixPlastexQuirks(texContents)
		texContents = self.getEmbeddedImages(texContents, sourceItem.title)
		texContents = self.burnInExtras(texContents)
		return texContents

	def fixPlastexQuirks(self,text):
		#Stop markdown from listifying things.
		reItemList = re.compile(r'<p>\s*([\(\[]*)([A-z0-9]{1,3})([\)\]\.\:])')
		text = reItemList.sub(lambda m: '<p>'+m.group(1)+m.group(2)+"\\"+m.group(3), text)

		#Stop pandoc from interpreting plastex output as code
		reStartSpaces = re.compile(r'^ +',re.M)
		text = reStartSpaces.sub('', text)
		reSmartQuotes = re.compile(r'`(.*?)\'')
		text = reSmartQuotes.sub(lambda m:"\'"+m.group(1)+"\'", text)

		#Remove empty paragraphs
		reEmptyP = re.compile(r'<p></p>')
		text = reEmptyP.sub('', text)

		return text

	def getTikzTemplateArgs(self):
		if 'tikz_template' in self.config.keys():
			tikzPath = os.path.join(self.config["tikz_template"])
			logger.debug('Using tikz template: %s'%tikzPath)
			return "--tikz-template=%s"%tikzPath
		else:
			return ""

	def runPlastex(self, source):
		logger.debug(source)
		outPath = os.path.join(self.root_dir, self.tmpDir)
		inPath = os.path.join(self.root_dir, source)

		cmd = 'plastex --dir={outPath} {tikzArgs} --sec-num-depth=3 --toc-depth=3 --split-level=-1 --toc-non-files --renderer=HTML5ncl {inPath} 2>&1'.format(outPath=outPath, tikzArgs=self.getTikzTemplateArgs(), inPath=inPath)

		logger.info('Running plastex: %s'%cmd)
		proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
		logger.debug(proc.stdout.read())
		proc.stdout.close()

		rc = proc.wait()
		if rc != 0:
			sys.stderr.write("Error: Something went wrong with the latex compilation! Quitting...\n")
			sys.stderr.write("(Use -vv for more information)\n")
			sys.exit(2)
		else:
			logger.info('Done!')


	def getEmbeddedImages(self,texContents,title):
		logger.info('    Moving embedded images:')
		#Markdown Images
		mdImage = re.compile(r'!\[[^\]]*\]\(([^\)]*)\)')
		for m in re.finditer(mdImage, texContents):
			inFile = os.path.basename(m.group(1))
			inPath = os.path.join(self.root_dir,self.tmpDir,'images',inFile)
			outPath = os.path.join(self.config['build_dir'],'static',title,inFile)
			outDir  = os.path.join(self.config['build_dir'],'static',title)
			logger.info('        %s=> %s'%(inPath,outPath))
			#ACTUALLY MOVE THE FILE
			mkdir_p(outDir)
			shutil.copyfile(inPath.strip(), outPath.strip())
			texContents = texContents.replace(m.group(1),os.path.join(self.config['build_dir'],'static',title, inFile))

		#Tikz Images
		tikzImage = re.compile(r'<object class=\"tikzpicture\" data=\"([^\)]*)\" type=\"image/svg\+xml\">')
		for m in re.finditer(tikzImage, texContents):
			inFile = os.path.basename(m.group(1))
			inPath = os.path.join(self.root_dir,self.tmpDir,'images',inFile)
			outPath = os.path.join(self.config['build_dir'],'static',title,inFile)
			outDir  = os.path.join(self.config['build_dir'],'static',title)
			logger.info('        %s=> %s'%(inPath,outPath))
			#ACTUALLY MOVE THE FILE
			mkdir_p(outDir)
			shutil.copyfile(inPath.strip(), outPath.strip())
			texContents = texContents.replace(m.group(1),os.path.join(self.config['build_dir'],'static',title, inFile))

		return texContents
	
