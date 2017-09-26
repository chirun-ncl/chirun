import logging
from . import hackmd
from . import latex
from . import pandoc
from . import plastex
from . import slides
from .item import load_item
import os
import re
import sys
from makeCourse import *

logger = logging.getLogger(__name__)

class CourseProcessor:

	def temp_path(self, path):
		tmp_dir = 'tmp'
		if not os.path.exists(tmp_dir):
			os.makedirs(tmp_dir)
		tpath = None
		while tpath is None or os.path.exists(tpath):
			tpath = os.path.join(tmp_dir,'{}-{}'.format(os.urandom(2).encode('hex'),path))
		self.config['tempFiles'].append(tpath)
		return tpath

	def replaceLabels(self,mdContents):
		for l in gen_dict_extract('label',self.config):
			mdLink = re.compile(r'\[([^\]]*)\]\('+l['label']+r'\)')
			mdContents = mdLink.sub(lambda m: "[" + m.group(1)+"]("+self.config['web_dir']+l['outFile']+".html)", mdContents)
		return mdContents

	def relativiseImages(self,mdContents):
		mdImageDir = os.path.join(self.config['build_dir'],'static')
		relativeImageDir = self.config['web_dir']+"static"
		mdContents = mdContents.replace(mdImageDir, relativeImageDir)
		return mdContents

	def getVimeoHTML(self, code):
		return '<iframe src="https://player.vimeo.com/video/'+code+'" width="100%" height="360" frameborder="0" webkitallowfullscreen \
				mozallowfullscreen allowfullscreen></iframe>'
	def getYoutubeHTML(self, code):
		return '<iframe width="100%" height="360" src="https://www.youtube.com/embed/'+code+'?ecver=1" frameborder="0" allowfullscreen></iframe>'
	def getNumbasHTML(self, URL):
		return '<iframe width="100%" height="1000px" src="'+URL+'" frameborder="0"></iframe>'
	def getSlidesHTML(self, code):
		hackmd.getSlidesPDF(self.config,code)
		return '<iframe src="'+HACKMD_URL+'/p/'+code+'/" style="overflow:hidden;" width="100%" height="480px" scrolling=no frameborder="0">\
				</iframe><div class="pad-top-10 pull-right"><a href="'+self.config['web_dir']+'static/'+code+'.pdf"><i class="fa fa-file-pdf-o" aria-hidden="true"></i> Download</a> \
				|&nbsp;<a target="_blank" href="'+HACKMD_URL+'/p/'+code+'/"><i class="fa fa-arrows-alt" aria-hidden="true"></i> Fullscreen</a></div>'
	def getSlidesURL(self,code):
		hackmd.getSlidesPDF(self.config,code)
		return HACKMD_URL+'/p/'+code+'/'

	def burnInExtras(self,mdContents,pdf=False):

		reVimeo = re.compile(r'{%vimeo\s*([\d\D]*?)\s*%}')
		reYoutube = re.compile(r'{%youtube\s*([\d\D]*?)\s*%}')
		reNumbas = re.compile(r'{%numbas\s*([^%{}]*?)\s*%}')
		reSlides = re.compile(r'{%slides\s*([^%{}]*?)\s*%}')
		if pdf:
			mdContents = reVimeo.sub(lambda m: "\n\n\url{https://vimeo.com/"+m.group(1)+"}", mdContents)
			mdContents = reYoutube.sub(lambda m: "\n\n\url{https://www.youtube.com/watch?v="+m.group(1)+"}", mdContents)
			mdContents = reNumbas.sub(lambda m: "\n\n\url{"+m.group(1)+"}", mdContents)
			mdContents = reSlides.sub(lambda m: "\n\n\url{"+self.getSlidesURL(m.group(1))+"}", mdContents)
		else:
			mdContents = reVimeo.sub(lambda m: self.getVimeoHTML(m.group(1)), mdContents)
			mdContents = reYoutube.sub(lambda m: self.getYoutubeHTML(m.group(1)), mdContents)
			mdContents = reNumbas.sub(lambda m: self.getNumbasHTML(m.group(1)), mdContents)
			mdContents = reSlides.sub(lambda m: self.getSlidesHTML(m.group(1)), mdContents)
			mdContents = self.relativiseImages(mdContents)

		mdContents = self.replaceLabels(mdContents)
		return mdContents

	def makePDF(self,item):
		_, ext = os.path.splitext(item.source)
		if ext == '.tex':
			latex.runPdflatex(self,item)
		else:
			self.run_pandoc(item,template_file='notes.latex', format='pdf')

	def doProcess(self):
		logger.info('Preprocessing Structure...')
		self.structure = [load_item(self,obj) for obj in self.config['structure']]

		logger.info('Deep exploring Structure...')

		for obj in self.structure:
			if obj.is_hidden:
				continue
			if obj.type == 'introduction':
				logger.info('Building index')
				self.run_pandoc(obj)

			elif obj.type == 'part':
				mkdir_p(os.path.join(self.config['build_dir'],obj.out_file))
				self.run_pandoc(obj)
				for chapter in obj.content:
					if(chapter.type != 'chapter'):
						raise Exception("Error: Parts must contain only chapters. {} is a {}".format(chapter.title, chapter.type))
					self.config['partsEnabled'] = True
					if chapter.is_hidden:
						continue
					self.run_pandoc(chapter)
					if self.config["build_pdf"]:
						self.makePDF(chapter)

			elif obj.type == 'chapter':
				if self.config['partsEnabled']:
					raise Exception("Error: Both parts and chapters found at top level. To fix: put all chapters inside parts or don't include parts at all. Quitting...\n")
				self.run_pandoc(obj)
				if self.config["build_pdf"]:
						self.makePDF(obj)

		logger.info('Done!')

	def load_tex(self, source, out_path):
		tmpDir = self.temp_path('plastex')
		plastex.runPlastex(self.config, source, tmpDir)
		texContents = open(os.path.join(self.root_dir, tmpDir, "index.html"), 'r').read()
		texContents = plastex.fixPlastexQuirks(texContents)
		texContents = plastex.getEmbeddedImages(self.config, texContents, tmpDir, out_path)
		texContents = self.burnInExtras(texContents)
		return texContents
