import logging
import os
import pkg_resources
import re
import sys
from makeCourse import *
from subprocess import Popen, PIPE

logger = logging.getLogger(__name__)

def runPandocForPart(course_config,part,inFile):
	outPath = os.path.join(course_config['build_dir'],part['outFile']+".html")
	templateFile = os.path.join(course_config['themes_dir'],course_config['theme'],'part.html')
	inPath = os.path.join(course_config['args'].dir,inFile)
	logger.info('    %s => %s'%(inFile,outPath))
	cmd = 'pandoc -markdown -s --title-prefix="%s" \
		--mathjax=https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS-MML_HTMLorMML \
		--toc --toc-depth=2 --section-divs --metadata date="`date`" %s -V web_dir=%s --template %s %s -o %s'\
		%(course_config['title'],'-V mocktest='+getMockTest(course_config) if containsMockTest(course_config) else '',course_config['web_dir'],templateFile,inPath,outPath)
	proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	logger.debug('    %s'%cmd )
	logger.debug(proc.stdout.read())
	proc.stdout.close()
	rc = proc.wait()
	if rc != 0:
		sys.stderr.write("Error: Something went wrong running pandoc! Quitting...\n")
		sys.stderr.write("(Use -vv for more information)\n")
		sys.exit(2)

def runPandocForChapter(course_config,ch,inFile):
	outPath = os.path.join(course_config['build_dir'],ch['outFile']+".html")
	templateFile = os.path.join(course_config['themes_dir'],course_config['theme'],'chapter.html')
	inPath = os.path.join(course_config['args'].dir,inFile)
	logger.info('    %s => %s'%(inFile,outPath))
	cmd = 'pandoc -markdown -s --title-prefix="%s" \
		--mathjax=https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS-MML_HTMLorMML \
		--toc --toc-depth=2 --section-divs --metadata date="`date`" %s -V web_dir=%s --template %s %s -o %s'\
		%(course_config['title'],'-V mocktest='+getMockTest(course_config) if containsMockTest(course_config) else '',course_config['web_dir'],templateFile,inPath,outPath)
	proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	logger.debug('    %s'%cmd )
	logger.debug(proc.stdout.read())
	proc.stdout.close()
	rc = proc.wait()
	if rc != 0:
		sys.stderr.write("Error: Something went wrong running pandoc! Quitting...\n")
		sys.stderr.write("(Use -vv for more information)\n")
		sys.exit(2)


def runPandocForChapterPDF(course_config,ch,inFile):
	outPath = os.path.join(course_config['build_dir'],ch['outFile']+".pdf")
	templateFile = os.path.join(course_config['themes_dir'],course_config['theme'],'notes.latex')
	inPath = os.path.join(course_config['args'].dir,inFile)
	logger.info('    %s => %s'%(inFile,outPath))
	cmd = 'pandoc -markdown --title-prefix="%s" -V chapter-name="%s" --metadata date="`date`" --listings --template %s %s -o %s'%(course_config['title'],ch['title'],templateFile,inPath,outPath)
	proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	logger.debug('    %s'%cmd )
	logger.debug(proc.stdout.read())
	proc.stdout.close()
	rc = proc.wait()
	if rc != 0:
		sys.stderr.write("Error: Something went wrong running pandoc! Quitting...\n")
		sys.stderr.write("(Use -vv for more information)\n")
		sys.exit(2)

def runPandocForIntro(course_config,ch,inFile):
	outPath = os.path.join(course_config['build_dir'],"index.html")
	templateFile = os.path.join(course_config['themes_dir'],course_config['theme'],'index.html')
	inPath = os.path.join(course_config['args'].dir,inFile)
	logger.info('    %s => %s'%(inFile,outPath))
	cmd = 'pandoc -markdown -s --title-prefix="%s" \
		--mathjax=https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS-MML_HTMLorMML \
		--toc --toc-depth=2 --section-divs --metadata date="`date`" %s -V web_dir=%s --template %s %s -o %s'\
		%(course_config['title'],'-V mocktest='+getMockTest(course_config) if containsMockTest(course_config) else '',course_config['web_dir'],templateFile,inPath,outPath)
	proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	logger.debug('    %s'%cmd )
	logger.debug(proc.stdout.read())
	proc.stdout.close()
	rc = proc.wait()
	if rc != 0:
		sys.stderr.write("Error: Something went wrong running pandoc! Quitting...\n")
		sys.stderr.write("(Use -vv for more information)\n")
		sys.exit(2)


if __name__ == "__main__":
    pass
