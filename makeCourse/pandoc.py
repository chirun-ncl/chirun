import logging
import os
import pkg_resources
import re
import sys
import datetime
from makeCourse import *
from subprocess import Popen, PIPE

logger = logging.getLogger(__name__)

class PandocRunner:
	def run_pandoc(self, item, template_file=None,out_format='html',force_local=False):
		if force_local:
			root = self.config['local_root']
			root_index = self.config['local_root_index']
		else:
			root = self.config['web_root']
			root_index = self.config['web_root_index']

		outPath = os.path.join(self.config['build_dir'], item.out_file+'.'+out_format)
		if template_file is None:
			template_file = item.template_file
		template_path = os.path.join(self.config['themes_dir'], self.config['theme'], template_file)
		date = datetime.date.today()

		logger.info('    {src} => {dest}'.format(src=item.title, dest=outPath))

		if template_file=='slides.revealjs':
			cmd = [
				'pandoc', '--mathjax={}'.format(self.mathjax_url),
				'-i', '-t', 'revealjs', '-s',
				'-V','revealjs-url={}/static/reveal.js'.format(root),
				'-V', 'web_root={}'.format(root), 
				'-V', 'web_root_index={}'.format(root_index),
				'--template', template_path, 
				'-o', outPath,
			]
		else:
			cmd = [
				'pandoc', '-s', '--toc','--toc-depth=2', '--section-divs', '--listings',
				'--title-prefix={}'.format(self.config['title']), '--mathjax={}'.format(self.mathjax_url),  
				'--metadata=date:{}'.format(date),
				'-V', 'web_root={}'.format(root), 
				'-V', 'web_root_index={}'.format(root_index),
				'--template', template_path, 
				'-o', outPath,
			]

		content = item.markdown(force_local=force_local,out_format=out_format).encode('utf-8')
		proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)

		try:
			outs, errs = proc.communicate(content)
		except:
			proc.kill()
			outs, errs = proc.communicate()

		if outs:
			logger.debug(outs.decode('utf-8'))
		if errs:
			logger.error(errs.decode('utf-8'))
			logger.error("Something went wrong running pandoc! Quitting...")
			logger.error("(Use -vv for more information)")
			sys.exit(2)

if __name__ == "__main__":
	pass
