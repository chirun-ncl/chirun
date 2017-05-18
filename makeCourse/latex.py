import os
from datetime import datetime
import glob
import sys
import pkg_resources
import shutil
from subprocess import Popen, PIPE 
from jinja2 import Template

def runPlastex(args,course_config,themePath,themeName,texFile):
	buildDir = os.path.join(args.dir,'build')
	cmd = 'HTML5TEMPLATES="%s" plastex --dir=%s --renderer=HTML5ncl --dollars --theme %s %s' \
				%(themePath,buildDir,themeName,texFile)
	if args.verbose:
		print 'Running plastex: %s'%cmd
	proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	if args.veryverbose:
		for line in iter(proc.stderr.readline, ''):
			print line
		proc.stdout.close()
	rc = proc.wait()
	if rc != 0:
		sys.stderr.write("Error: Something went wrong with the latex compilation! Quitting...\n")
		sys.stderr.write("(Use -vv for more information)\n")
		sys.exit(2)
	elif args.verbose:
		print 'Done!'
	
def copyWebsetupSty(args):
	resource_package = "makeCourse"
	resource_path = '/'.join(('misc', 'websetup.sty'))
	webStyPath = pkg_resources.resource_filename(resource_package, resource_path)
	target = os.path.join(args.dir,'websetup.sty')

	if args.verbose:
		print "    ", webStyPath, "=>", target
	shutil.copy (webStyPath, target)
	return target

def buildMainTex(args,course_config):
	mainTexPath = os.path.join(args.dir,'main-%s.tex'%os.urandom(2).encode('hex'))
	if args.verbose:
		print 'Building .tex file: %s'%	mainTexPath
	resource_package = "makeCourse"
	resource_path = '/'.join(('misc', 'main.jinja2'))
	mainTexTemplate = pkg_resources.resource_string(resource_package, resource_path)
	t = Template(mainTexTemplate)
	mainTexRendered = t.render(course = course_config)
	f = open(mainTexPath,"w") 
	f.write(mainTexRendered) 
	f.close() 
	return mainTexPath

def doLatexProcess(args,course_config):
	if 'themePath' in course_config.keys():
		themePath = course_config['themePath']
	elif os.path.isabs(args.dir):
		themePath = args.dir
	else:
		themePath = os.path.join(os.getcwd(),args.dir)

	if 'theme' in course_config.keys():
		themeName = course_config['theme']
	else:
		themeName = 'default'

	if args.verbose:
		print 'Copying web style file websetup.sty...'	
	newWebStyPath = copyWebsetupSty(args)

	if args.verbose:
		print 'Building complete .tex...'
	mainTexPath = buildMainTex(args, course_config)
	
	runPlastex(args,course_config,themePath,themeName,mainTexPath)

	if args.verbose:
		print 'Cleaning Up...'
	for paux_file in glob.glob("*.paux"):
		if args.verbose:
			print '    Deleted: %s'%paux_file
		os.remove(paux_file)
	if args.verbose:
		print '    Deleted: %s'%newWebStyPath
	os.remove(newWebStyPath)
	if args.verbose:
		print '    Deleted: %s'%mainTexPath
	os.remove(mainTexPath)

	if args.verbose:
		print 'Done!'

if __name__ == "__main__":
    pass
