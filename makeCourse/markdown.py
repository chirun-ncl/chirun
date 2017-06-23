import os
import re
from datetime import datetime
import glob
import sys
import pkg_resources
import shutil
from subprocess import Popen, PIPE 
from distutils.dir_util import copy_tree

def runPandoc(args,course_config,themePath,themeName):
	buildDir = os.path.join(args.dir,'build')
	for obj in course_config['structure']:
		if obj['type'] == 'introduction':
			templateFile = os.path.join(themePath,themeName,'index.html')
		else:
			templateFile = os.path.join(themePath,themeName,'template.html')
		outName = re.sub(r'.md$','.html',obj['source'])
		outName = re.sub(r'^[0-9A-z][0-9A-z][0-9A-z][0-9A-z]-','',outName)
		outPath = os.path.join(buildDir,outName)
		if args.verbose:
			print '    %s => %s'%(obj['source'],outPath)
		cmd = 'pandoc -s --title-prefix="%s" \
			--mathjax=https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS_CHTML \
			--css=%s --toc --toc-depth=1 --section-divs --metadata date="`date`" --template %s %s -o %s'\
			%(course_config['title'],os.path.join(course_config['static_dir'],'styles.css'),\
			templateFile,os.path.join(args.dir,obj['source']),outPath)

		proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
		if args.veryverbose:
			print '    %s'%cmd 
			for line in iter(proc.stderr.readline, ''):
				print line
			proc.stdout.close()
		rc = proc.wait()
		if rc != 0:
			sys.stderr.write("Error: Something went wrong with the markdown compilation! Quitting...\n")
			sys.stderr.write("(Use -vv for more information)\n")
			sys.exit(2)
	if args.verbose:
		print 'Done!'
	
def runPdflatex(args,obj,sourcePath,pdfPath):
	sourcePathDir = os.path.dirname(sourcePath)
	pdfPathDir = os.path.abspath(os.path.dirname(pdfPath))
	cmd = 'cd %s && pdflatex %s && mkdir -p %s && cp main.pdf %s'\
			%(sourcePathDir,'main.tex',pdfPathDir,pdfPathDir)
	if args.veryverbose:
		print 'Running pdflatex: %s'%cmd
	proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	if args.veryverbose:
		for line in iter(proc.stdout.readline, ''):
			print line
		proc.stdout.close()
	rc = proc.wait()
	if rc != 0:
		sys.stderr.write("Error: Something went wrong with the latex compilation! Quitting...\n")
		sys.stderr.write("(Use -vv for more information)\n")
		sys.exit(2)
	elif args.veryverbose:
		print 'Done!'

def slugify(value):
	return "".join([c for c in re.sub(r'\s+','_',value) if c.isalpha() or c.isdigit() or c=='_'])\
				.rstrip().lower()

def injectYAMLheader(args,course_config,title,mdContents):
	if title == 'index':
		header = "---\ntitle: %s\nauthor: %s\nchapters:\n"%(title,course_config['author'])
		for obj in course_config['structure']:
			if obj['type'] == 'chapter':
				header += "    - title: %s\n"%obj['title']
				header += "      slug: %s\n"%slugify(obj['title'])
		header += "\n---\n\n"
	else:
		header = "---\ntitle: %s\nauthor: %s\n\n---\n\n"%(title,course_config['author'])
	return header + mdContents

def buildMDFiles(args,course_config):
	if args.verbose:
		print 'Building temporary .md files where required...'

	combinedChapterStructure = list()
	tempSourceFiles = list()

	for obj in course_config['structure']:
		if obj['type'] == 'introduction':
			obj['title'] = 'index'
		if isinstance(obj['source'], list):
			combinedMDContents = ''
			for origMdFile in obj['source']:
				mdContents = open(os.path.join(args.dir,origMdFile), 'r').read()
				mdContents = re.sub(r'^---.*?---','',mdContents,flags=re.S) #strip YAML headers
				combinedMDContents += '\n'+mdContents
			newFile = '%s-%s.md'%(os.urandom(2).encode('hex'),slugify(obj['title']))
			obj['source'] = newFile
			tempSourceFiles.append(newFile)
			if args.verbose:
				print '    Combining %s => %s'%(obj['title'],newFile)
			combinedMDContents = injectYAMLheader(args,course_config,obj['title'],combinedMDContents)
			f = open(os.path.join(args.dir,newFile), 'w') 
			f.write(combinedMDContents)
			f.close()
		else:
			origMdFile = obj['source']
			mdContents = open(os.path.join(args.dir,origMdFile), 'r').read()
			if mdContents[:3] != '---':
				newFile = '%s-%s.md'%(os.urandom(2).encode('hex'),slugify(obj['title']))
				obj['source'] = newFile
				tempSourceFiles.append(newFile)
				if args.verbose:
					print '    %s => %s'%(origMdFile,newFile)
				mdContents = injectYAMLheader(args,course_config,obj['title'],mdContents)
				f = open(os.path.join(args.dir,newFile), 'w')
				f.write(mdContents)
				f.close()

	return tempSourceFiles 

def doMarkdownProcess(args,course_config):
	if 'themePath' in course_config.keys():
		themePath = course_config['themePath']
	else:
		themePath = os.path.join(args.dir,'Themes')

	if 'theme' in course_config.keys():
		themeName = course_config['theme']
	else:
		themeName = 'default'

	tempSourceFiles = buildMDFiles(args, course_config)

	if args.verbose:
		print 'Running pandoc...'

	runPandoc(args,course_config,themePath,themeName)

	srcPath = os.path.join(themePath,themeName,'static')
	dstpath = os.path.join(args.dir,course_config['static_dir'])
	if args.verbose:
		print 'Copying Theme\'s static files to the course static directory'
		print "    %s => %s"%(srcPath,dstpath)
	copy_tree(srcPath, dstpath)

	if args.verbose:
		print 'Cleaning up after pandoc...'
	for temp_file in tempSourceFiles:
		if args.verbose:
			print '    Deleted: %s'%temp_file
		os.remove(os.path.join(args.dir,temp_file))

	if args.verbose:
		print 'Done!'

def doLatexPDFProcess(args,course_config):
	if 'static_dir' in course_config.keys():
		staticPath = course_config['static_dir']
	else:
		staticPath = 'static'

	if args.verbose:
		print 'Building .pdf files...'

	for obj in course_config['structure']:
		if obj['type'] == 'include' and 'content.tex' in obj['source']:
			sourcePath = os.path.join(args.dir,obj['source'])
			pdfPath = os.path.join(args.dir,staticPath,obj['source'].replace("content.tex", "main.pdf"))
			if args.verbose:
				print '    %s => %s'%(sourcePath, pdfPath)
			runPdflatex(args,obj,sourcePath,pdfPath)	
	
	if args.verbose:
		print 'Cleaning up after pdflatex...'
	for obj in course_config['structure']:
		if obj['type'] == 'include' and 'content.tex' in obj['source']:
			compilePath = os.path.join(args.dir,obj['source'].replace("content.tex", "main"))
			if args.verbose:
				print '    Deleted: %s.log'%compilePath
				print '    Deleted: %s.aux'%compilePath
				print '    Deleted: %s.out'%compilePath
				print '    Deleted: %s.pdf'%compilePath
			os.remove('%s.log'%compilePath)
			os.remove('%s.aux'%compilePath)
			os.remove('%s.out'%compilePath)
			os.remove('%s.pdf'%compilePath)
	if args.verbose:
		 print 'Done!'
if __name__ == "__main__":
    pass
