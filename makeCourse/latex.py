import os
import glob
import sys
from subprocess import Popen, PIPE 

def runPlastex(args,course_config,themePath,themeName,texFile):
	cmd = 'HTML5TEMPLATES="%s" plastex --dir=%s/build/ --renderer=HTML5ncl --dollars --theme %s %s/%s' \
				%(themePath,args.dir,themeName,args.dir,texFile)
	if args.verbose:
		print 'running plastex: %s'%cmd
	proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	if args.veryverbose:
		for line in iter(proc.stderr.readline, ''):
			print line
		proc.stdout.close()
	rc = proc.wait()
	if rc != 0:
		sys.stderr.write("Error: Something went wrong with the latex compilation! Quitting...\n")
		sys.stderr.write("(Use -v for more information)\n")
		sys.exit(2)
	elif args.verbose:
		print 'Done!'
	

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

	if 'head_tex' in course_config.keys():
		texFile = course_config['head_tex']
	else:
		texFile = args.dir+'.tex'

	runPlastex(args,course_config,themePath,themeName,texFile)

	if args.verbose:
		print 'Cleaning Up...'
	for paux_file in glob.glob("*.paux"):
		if args.verbose:
			print '    %s'%paux_file
		os.remove('%s'%paux_file)
	if args.verbose:
		print 'Done!'

if __name__ == "__main__":
    pass
