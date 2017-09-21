import logging
import makeCourse.hackmd
import makeCourse.latex
import makeCourse.pandoc
import makeCourse.plastex
import makeCourse.slides
import os
import re
import sys
from makeCourse import *

logger = logging.getLogger(__name__)

class CourseProcessor:

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
		makeCourse.hackmd.getSlidesPDF(self.config,code)
		return '<iframe src="'+HACKMD_URL+'/p/'+code+'/" style="overflow:hidden;" width="100%" height="480px" scrolling=no frameborder="0">\
				</iframe><div class="pad-top-10 pull-right"><a href="'+self.config['web_dir']+'static/'+code+'.pdf"><i class="fa fa-file-pdf-o" aria-hidden="true"></i> Download</a> \
				|&nbsp;<a target="_blank" href="'+HACKMD_URL+'/p/'+code+'/"><i class="fa fa-arrows-alt" aria-hidden="true"></i> Fullscreen</a></div>'
	def getSlidesURL(self,code):
		makeCourse.hackmd.getSlidesPDF(self.config,code)
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

	def createIndexYAMLheader(self):
		def chapter_yaml(ch):
			return {
				'title': ch['title'],
				'slug': slugify(ch['title']),
			}

		def link_yaml(s):
			if isHidden(s):
				return
			if s['type'] == 'part':
				return {
					'title': s['title'],
					'slug': slugify(s['title']),
					'chapters': [chapter_yaml(ch) for ch in s['content'] if not isHidden(ch)]
				}
			elif s['type'] == 'chapter':
				return {
					'title': s['title'],
					'slug': slugify(s['title']),
				}

		header = {
			'title': 'index',
			'author': self.config['author'],
			'links': [x for x in [link_yaml(s) for s in self.config['structure']] if x is not None],
		}

		return yaml_header(header)

	def createYAMLheader(self,obj,part=False):
		def chapter_yaml(ch,active=False):
			d = {
				'title': ch['title'],
				'file': '{}.html'.format(ch['outFile']),
				'pdf': '{}.pdf'.format(ch['outFile']),
			}
			if active:
				d['active'] = 1
			return d

		header = {
			'title': obj['title'],
			'build_pdf': self.config['build_pdf'],
			'author': self.config['author'],
			'slug': slugify(obj['title']),
		}
		if part:
			header['part'] = part['title']
			header['part-slug'] = slugify(part['title'])
			header['chapters'] = [chapter_yaml(ch,ch==obj) for ch in part['content'] if not isHidden(ch)]
		else:
			header['chapters'] = [chapter_yaml(ch,ch==obj) for ch in self.config['structure'] if not isHidden(ch)]

		return yaml_header(header)

	def createPartYAMLheader(self,obj):	
		def chapter_yaml(ch):
			return {
				'title': ch['title'],
				'slug': slugify(ch['title']),
			}

		header = {
			'title': obj['title'],
			'author': self.config['author'],
			'part-slug': slugify(obj['title']),
			'chapters': [chapter_yaml(ch) for ch in obj['content'] if not isHidden(ch)],
		}

		return yaml_header(header)

	def buildpartMDFile(self,part):
		newFile = temp_path('%s.md' % slugify(part['title']))
		self.config['tempFiles'].append(newFile)
		newFileContent = self.createPartYAMLheader(part)
		f = open(os.path.join(self.config['args'].dir,newFile), 'w')
		f.write(newFileContent)
		f.close()
		return newFile

	def buildIntroMDFile(self,obj):
		newFile = temp_path('index.md')
		self.config['tempFiles'].append(newFile)
		newFileContent = self.createIndexYAMLheader()

		logger.info('Building index: %s'%newFile)

		if obj['source'][-3:] == '.md':
			mdContents = open(os.path.join(self.config['args'].dir,obj['source']), 'r').read()
			if mdContents[:3] != '---':
				logger.debug('    Burning in iframes & extras.')
				mdContents = self.burnInExtras(mdContents)
				newFileContent += '\n\n' + mdContents
			else:
				sys.stderr.write("Error: Markdown file %s contains unsupported YAML header. Please remove the header, I'll make one automatically. Quitting...\n"%obj['source'])
				sys.exit(2)
		elif obj['source'][-4:] == '.tex':
			#Do latex -> html snippet
			tmpDir = temp_path('plastex-index')
			self.config['tempFiles'].append(tmpDir)
			makeCourse.plastex.runPlastex(self.config,obj['source'],tmpDir)
			texContents = open(os.path.join(self.config['args'].dir,tmpDir,"index.html"), 'r').read()
			texContents = makeCourse.plastex.fixPlastexQuirks(texContents)
			texContents = makeCourse.plastex.getEmbeddedImages(self.config,texContents,tmpDir,"index")
			texContents = self.burnInExtras(texContents)
			newFileContent += '\n\n' + texContents
		elif re.search(r'[^/\?:\s]+', obj['source']):
			code = re.search(r'([^/\?:\s]+)', obj['source']).group(1)
			mdContents = makeCourse.hackmd.getHackmdDocument(self.config,code)
			mdContents = makeCourse.hackmd.getEmbeddedImages(self.config,mdContents)
			newFileContent += '\n\n' + mdContents
		else:
			sys.stderr.write("Error: Unrecognised source type for index. Quitting...\n")
			sys.exit(2)

		f = open(os.path.join(self.config['args'].dir,newFile), 'w')
		f.write(newFileContent)
		f.close()

		if 'source' not in obj.keys():
			sys.stderr.write("Error: No source defined for introduction... Quitting...\n")
			sys.exit(2)

		return newFile

	def buildChapterMDFile(self,ch,part=False,pdf=False):
		if 'content' in ch and 'source' in ch:
			sys.stderr.write("Error: Chapter %s contains both content and source elements; including both is invalid. Quitting...\n"%ch['title'])
			sys.exit(2)

		if 'source' in ch.keys():
			if part:
				newFile = temp_path('%s_%s.md'%(slugify(part['title']),slugify(ch['title'])))
			else:
				newFile = temp_path('%s.md' % slugify(ch['title']))
			self.config['tempFiles'].append(newFile)
			newFileContent = self.createYAMLheader(ch,part)

			logger.info('Building chapter file: %s'%newFile)

			if ch['source'][-3:] == '.md':
				logger.info('    Adding: %s'%ch['title'])
				mdContents = open(os.path.join(self.config['args'].dir,ch['source']), 'r').read()
				if mdContents[:3] == '---':
					logger.info('    Note: Markdown file %s contains a YAML header. Stripping it...'%ch['source'])
					mdContents = re.sub(r'^---.*?---\n','',mdContents,re.S)
				logger.debug('    Burning in iframes & extras.')
				mdContents = self.burnInExtras(mdContents,pdf)
				newFileContent += '\n\n' + mdContents
			elif ch['source'][-4:] == '.tex':
				#Do latex -> html snippet
				tmpDir = temp_path('plastex-%s'%slugify(ch['title']))
				self.config['tempFiles'].append(tmpDir)
				makeCourse.plastex.runPlastex(self.config,ch['source'],tmpDir)
				texContents = open(os.path.join(self.config['args'].dir,tmpDir,"index.html"), 'r').read()
				texContents = makeCourse.plastex.fixPlastexQuirks(texContents)
				texContents = makeCourse.plastex.getEmbeddedImages(self.config,texContents,tmpDir,ch['outFile'])
				texContents = self.burnInExtras(texContents)
				newFileContent += '\n\n' + texContents
			elif re.search(r'[^/\?:\s]+', ch['source']):
				code = re.search(r'([^/\?:\s]+)', ch['source']).group(1)
				mdContents = makeCourse.hackmd.getHackmdDocument(self.config,code)
				mdContents = makeCourse.hackmd.getEmbeddedImages(self.config,mdContents)
				logger.debug('    Burning in iframes & extras.')
				mdContents = self.burnInExtras(mdContents,pdf)
				newFileContent += '\n\n' + mdContents
			else:
				sys.stderr.write("Error: Unrecognised source type for %s:%s. Quitting...\n"%(ch['title'],ch['source']))
				sys.exit(2)

			f = open(os.path.join(self.config['args'].dir,newFile), 'w')
			f.write(newFileContent)
			f.close()

		return newFile

	def makePDF(self,ch,part=False):
		if ch['source'][-4:] == '.tex':
			inDir = os.path.join(self.config['args'].dir,os.path.dirname(ch['source']))
			inFile = os.path.basename(ch['source'])
			makeCourse.latex.runPdflatex(self.config,ch,inFile,inDir)
		else:
			chFileName = self.buildChapterMDFile(ch,part=part,pdf=True)
			makeCourse.pandoc.runPandocForChapterPDF(self.config,ch,chFileName)

	def doProcess(self):
		logger.info('Preprocessing Structure...')
		self.preProcessFilenames()

		logger.info('Deep exploring Structure...')

		for obj in self.config['structure']:
			if isHidden(obj): continue
			if obj['type'] == 'introduction':
				obj['title'] = 'index'
				inFileName = self.buildIntroMDFile(obj)
				makeCourse.pandoc.runPandocForIntro(self.config,obj,inFileName)
			elif obj['type'] == 'part':
				partFileName = self.buildpartMDFile(obj)
				makeCourse.pandoc.runPandocForPart(self.config,obj,partFileName)
				for ch in obj['content']:
					if(ch['type'] != 'chapter'):
						sys.stderr.write("Error: Parts must contain chapters. (%s) Quitting...\n"%obj['title'])
						sys.exit(2)
					self.config['partsEnabled'] = True
					if isHidden(obj): continue
					chFileName = self.buildChapterMDFile(ch,part=obj)
					makeCourse.pandoc.runPandocForChapter(self.config,ch,chFileName)
					if self.config["build_pdf"]:
						self.makePDF(ch,part=obj)
			elif obj['type'] == 'chapter':
				if self.config['partsEnabled']:
					sys.stderr.write("Error: Both parts and chapters found at top level. To fix: put all chapters inside parts or don't include parts at all. Quitting...\n")
					sys.exit(2)
				chFileName = self.buildChapterMDFile(obj)
				makeCourse.pandoc.runPandocForChapter(self.config,obj,chFileName)
				if self.config["build_pdf"]:
						self.makePDF(obj)
			elif obj['type'] == 'mocktest':
				#TODO: download a mock test from numbas
				pass

		logger.info('Done!')

	def preProcessFilenames(self):
		for obj in self.config['structure']:
			if obj['type'] == 'introduction':
				obj['title'] = 'index'
				obj['outFile']  = 'index.html'
			if obj['type'] == 'part':
				obj['outFile'] = slugify(obj['title'])
				if isHidden(obj): continue
				mkdir_p(os.path.join(self.config['build_dir'],obj['outFile']))
				for ch in obj['content']:
					ch['outFile'] = os.path.join(obj['outFile'],slugify(ch['title']))
			if obj['type'] == 'chapter':
				obj['outFile'] = slugify(obj['title'])
