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
		if self.parent:
			return [self.parent.slug,self.slug]
		else:
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
				logger.info('    Note: Markdown file {} contains a YAML header. It will be merged in...'.format(self.source))
				mdContents = re.sub(r'^---.*?---\n','',mdContents,re.S)
			logger.debug('    Burning in iframes & extras.')
			mdContents = self.course.burnInExtras(mdContents,pdf)
			return mdContents
		elif ext == '.tex':
			return self.course.load_latex_content(self)
		elif re.search(r'[^/\?:\s]+', self.source):
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

	@property
	def out_path(self):
		return [self.slug]

	def yaml(self,active=False):
		return {
			'title': self.title,
			'author': self.course.config['author'],
			'year': self.course.config['year'],
			'part-slug': self.slug,
			'slug': self.slug,
			'chapters': [item.yaml() for item in self.content if not item.is_hidden],
			'top_links': self.course.config['top_links'],
		}

	def markdown(self,**kwargs):
		return yaml_header(self.yaml())

class Url(Item):
	type = 'url'
	title = 'Untitled URL'
	template_file = 'part.html'

	def yaml(self,active=False):
		return {
			'title': self.title,
			'external_url': self.source,
		}

	def markdown(self,**kwargs):
		return None

class Chapter(Item):
	type = 'chapter'
	title = 'Untitled chapter'
	template_file = 'chapter.html'

	def yaml(self,active=False):
		d = {
			'title': self.title,
			'slug': self.slug,
			'build_pdf': self.course.config['build_pdf'],
			'author': self.course.config['author'],
			'year': self.course.config['year'],
			'file': '{}.html'.format(self.url),
			'slides': '{}.slides.html'.format(self.url),
			'pdf': '{}.pdf'.format(self.url),
			'top_links': self.course.config['top_links'],
		}
		if active:
			d['active'] = 1

		return d

	def markdown(self,pdf=False):
		header = self.yaml()

		if self.parent:
			header['part'] = self.parent.title
			header['part-slug'] = self.parent.slug
			header['chapters'] = [item.yaml(item==self) for item in self.parent.content if not item.is_hidden]
		else:
			header['chapters'] = [item.yaml(item==self) for item in self.course.structure if not item.type =='introduction' and not item.is_hidden]

		return yaml_header(header) + '\n\n' + self.get_content(pdf=pdf)

class Slides(Chapter):
	type = 'slides'
	title = 'Untitled Slides'
	template_file = 'slides.html'


class Introduction(Item):
	type = 'introduction'
	template_file = 'index.html'
	title = 'index'
	out_path = ['index']

	def yaml(self,active=False):
		return {
			'title': 'index',
			'author': self.course.config['author'],
			'year': self.course.config['year'],
			'top_links': self.course.config['top_links'],
		}

	def markdown(self,**kwargs):
		def link_yaml(s):
			if s.is_hidden:
				return
			return s.yaml()

		header = self.yaml()
		header['links'] = [link_yaml(s) for s in self.course.structure if not s.type =='introduction' and not s.is_hidden]
		
		if [s for s in self.course.structure if not s.type =='introduction' and not s.is_hidden][0].type == 'part':
			header['isPart'] = 1

		return yaml_header(header)+'\n\n'+self.get_content()

item_types = {
	'introduction': Introduction,
	'part': Part,
	'chapter': Chapter,
	'url': Url,
	'slides': Slides,
}

def load_item(course, data, parent=None):
	return item_types[data['type']](course, data, parent)
