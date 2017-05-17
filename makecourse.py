import yaml
import os
import sys
import argparse
from subprocess import Popen, PIPE 

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

	cmd = 'HTML5TEMPLATES="%s" plastex --dir=%s/build/ --renderer=HTML5ncl --dollars --theme %s %s/%s'%(themePath,args.dir,themeName,args.dir,texFile)
	if args.verbose:
		print 'running command:%s'%cmd
	proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	if args.verbose:
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

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-v', dest='verbose', action='store_true')
	parser.add_argument('dir', help='a course definition directory')
	args = parser.parse_args()

	if args.verbose:
		print "Running makecourse in directory %s"%args.dir
		print "Reading %s..."%os.path.join(args.dir,'config.yml')

	with open(os.path.join(args.dir,'config.yml'), 'r') as f:
		course_config = yaml.load(f)

	if args.verbose:
		print "Done!"
	
	if course_config['source_type'] == 'latex':
		if args.verbose:
			print "Starting Latex processing..."
		doLatexProcess(args,course_config)
	elif course_config['source_type'] == 'markdown':
		if args.verbose:
			print "Starting markdown processing..."
		doMarkdownProcess(args,course_config)
	else:
		sys.stderr.write("Error: Unrecognised source_type! Quitting...\n")
		sys.exit(2)

	if args.verbose:
		print "All done! Output written to %s"%os.path.join(args.dir,'build')
if __name__ == "__main__":
	main()