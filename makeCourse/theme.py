import os
import logging

logger = logging.getLogger(__name__)

class Theme(object):
	def __init__(self, course, theme_data, **kwargs):
		self.course = course
		self.hidden = False
		for key in theme_data:
			setattr(self, key, theme_data[key])
		for key in kwargs:
			setattr(self, key, kwargs[key])

	def __str__(self):
		return '{}'.format(self.title)

	def __repr__(self):
		return '<makeCourse.theme.Theme: {}>'.format(self.title)

	@property
	def source_path(self):
		return os.path.join(self.course.config['themes_dir'], self.source)

	@property
	def alt_themes_yaml(self):
		return [t.yaml for t in self.course.themes if not (t.hidden or t==self)]

	@property
	def yaml(self):
		return {
			'title': self.title,
			'source': self.source,
			'path': self.path,
			'hidden': self.hidden,
		}