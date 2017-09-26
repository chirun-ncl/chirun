import logging
import os
import re
from makeCourse import slugify, isHidden, yaml_header
from . import plastex
from . import hackmd

logger = logging.getLogger(__name__)

class Item(object):
	template_file = ''
	type = None

	def __init__(self, course, data, parent=None):
		self.course = course
		self.parent = parent
		self.data = data
		self.title = self.data.get('title',self.title)
		self.slug = slugify(self.title)
		self.source = self.data.get('source','')
		self.is_hidden = self.data.get('hidden',False)
		self.content = [load_item(course, obj, self) for obj in self.data.get('content',[])]

	def __str__(self):
		return '{} {}'.format(self.type, self.title)

	def markdown(self,**kwargs):
		raise NotImplementedError("Item does not implement the markdown method")

	@property
	def out_path(self):
		return [self.slug]

	@property
	def out_file(self):
		return os.path.join(*self.out_path)

	@property
	def url(self):
		return '/'.join(self.out_path)

	def get_content(self,pdf=False):
		logger.info('Building {} file: {}'.format(self.type, self.title))

		_, ext = os.path.splitext(self.source)

		if ext == '.md':
			mdContents = open(os.path.join(self.course.root_dir,self.source), 'r').read()
			if mdContents[:3] == '---':
				if self.allow_yaml_header:
					logger.info('    Note: Markdown file {} contains a YAML header. Stripping it...'.format(ch['source']))
					mdContents = re.sub(r'^---.*?---\n','',mdContents,re.S)
				else:
					raise Exception("Error: Markdown file {} contains unsupported YAML header. Please remove the header, I'll make one automatically.".format(self.source))
			logger.debug('    Burning in iframes & extras.')
			mdContents = self.course.burnInExtras(mdContents,pdf)
			return mdContents
		elif ext == '.tex':
			return self.course.load_tex(self.source,self.out_file)
		elif re.search(r'[^/\?:\s]+', ch['source']):
			code = re.search(r'([^/\?:\s]+)', self.source).group(1)
			mdContents = hackmd.getHackmdDocument(self.course.config,code)
			mdContents = hackmd.getEmbeddedImages(self.course.config,mdContents)
			logger.debug('    Burning in iframes & extras.')
			mdContents = self.course.burnInExtras(mdContents,pdf)
			return mdContents
		else:
			raise Exception("Error: Unrecognised source type for {}: {}.".format(ch.title,ch.source))

class Part(Item):
	type = 'part'
	title = 'Untitled part'
	template_file = 'part.html'

	def markdown(self,**kwargs):
		header = {
			'title': self.title,
			'author': self.course.config['author'],
			'part-slug': self.slug,
			'chapters': [{'title':ch.title, 'slug': ch.slug} for ch in self.content if not ch.is_hidden],
		}

		content = yaml_header(header)
		return content

class Chapter(Item):
	type = 'chapter'
	title = 'Untitled chapter'
	template_file = 'chapter.html'

	@property
	def out_path(self):
		if self.parent:
			return [self.parent.slug,self.slug]
		else:
			return [self.slug]

	def markdown(self,pdf=False):
		def chapter_yaml(ch,active=False):
			d = {
				'title': ch.title,
				'file': '{}.html'.format(ch.url),
				'pdf': '{}.pdf'.format(ch.url),
			}
			if active:
				d['active'] = 1
			return d

		header = {
			'title': self.title,
			'slug': self.slug,
			'build_pdf': self.course.config['build_pdf'],
			'author': self.course.config['author'],
		}
		if self.parent:
			header['part'] = self.parent.title
			header['part-slug'] = self.parent.slug
			header['chapters'] = [chapter_yaml(ch,ch==self) for ch in self.parent.content if not ch.is_hidden]
		else:
			header['chapters'] = [chapter_yaml(ch,ch==self) for ch in self.course.structure if not ch.is_hidden]

		return yaml_header(header) + '\n\n' + self.get_content(pdf=pdf)

class Introduction(Item):
	type = 'introduction'
	template_file = 'index.html'
	title = 'index'
	out_path = ['index']

	def markdown(self,**kwargs):
		def chapter_yaml(ch):
			return {
				'title': ch.title,
				'slug': ch.slug,
			}

		def link_yaml(s):
			if s.is_hidden:
				return
			if s.type == 'part':
				return {
					'title': s.title,
					'slug': s.slug,
					'chapters': [chapter_yaml(ch) for ch in s.content if not ch.is_hidden]
				}
			elif s.type == 'chapter':
				return {
					'title': s.title,
					'slug': s.slug,
				}

		header = {
			'title': 'index',
			'author': self.course.config['author'],
			'links': [x for x in [link_yaml(s) for s in self.course.structure] if x is not None],
		}

		return yaml_header(header)+'\n\n'+self.get_content()

item_types = {
	'introduction': Introduction,
	'part': Part,
	'chapter': Chapter,
}
def load_item(course, data, parent=None):
	return item_types[data['type']](course, data, parent)
