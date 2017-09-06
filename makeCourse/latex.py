import sys
import os
import re
import pkg_resources
from subprocess import Popen, PIPE 

def runPdflatex(course_config,ch,inFile,inDir=None):
	if not inDir:
		inDir = course_config['args'].dir
	baseFile = re.sub(r'.tex$','',inFile)
	cmd = 'cd %s && pdflatex %s && pdflatex %s'%(inDir,inFile,inFile)
	proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	if course_config['args'].verbose:
		print('Running pdflatex: %s'%cmd)
	if course_config['args'].veryverbose:
		for line in iter(proc.stdout.readline, ''):
			print(line)
		proc.stdout.close()
	rc = proc.wait()
	if rc != 0:
		sys.stderr.write("Error: Something went wrong running pdflatex! Quitting...\n")
		sys.stderr.write("(Use -vv for more information)\n")
		sys.exit(2)

	outPath = os.path.join(course_config['build_dir'],ch['outFile']+".pdf")
	if course_config['args'].verbose:
		print('    Copying pdf output: %s => %s'%(os.path.join(inDir,baseFile+'.pdf'),outPath))
	cmd = 'cp %s %s'%(os.path.join(inDir,baseFile+'.pdf'),outPath)
	proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	if course_config['args'].veryverbose:
		print('    %s'%cmd )
		for line in iter(proc.stdout.readline, ''):
			print(line)
		proc.stdout.close()
	rc = proc.wait()
	if rc != 0:
		sys.stderr.write("Error: Something went wrong copying resulting pdf! Quitting...\n")
		sys.stderr.write("(Use -vv for more information)\n")
		sys.exit(2)


	if course_config['args'].verbose:
		print('    Cleaning up after pdflatex...')
		print('        Deleting: %s.log'%os.path.join(course_config['args'].dir,baseFile))
		print('        Deleting: %s.aux'%os.path.join(course_config['args'].dir,baseFile))
		print('        Deleting: %s.out'%os.path.join(course_config['args'].dir,baseFile))
		print('        Deleting: %s.pdf'%os.path.join(course_config['args'].dir,baseFile))
		print('        Deleting: %s.snm'%os.path.join(course_config['args'].dir,baseFile))
		print('        Deleting: %s.nav'%os.path.join(course_config['args'].dir,baseFile))
		print('        Deleting: %s.toc'%os.path.join(course_config['args'].dir,baseFile))

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
