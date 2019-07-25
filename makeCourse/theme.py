import logging
from distutils.dir_util import copy_tree

logger = logging.getLogger(__name__)


class Theme(object):
    def __init__(self, course, name, source, theme_data):
        self.course = course
        self.hidden = False
        self.name = name
        self.source = source
        keys = ('title','path','hidden')
        for key in keys:
            if key in theme_data:
                setattr(self, key, theme_data[key])

    def __str__(self):
        return '{}'.format(self.title)

    def __repr__(self):
        return '<makeCourse.theme.Theme: {}>'.format(self.title)

    @property
    def template_path(self):
        return self.source / 'templates'

    def alt_themes_contexts(self):
        return [t.get_context() for t in self.course.themes if not (t.hidden or t == self)]

    def get_context(self):
        return {
            'title': self.title,
            'source': self.name,
            'path': self.path,
            'hidden': self.hidden,
        }

    def copy_static_files(self):
        srcPath = self.source / 'static'
        dstPath = self.course.get_build_dir() / 'static'

        logger.info("Copying theme's static directory to the build's static directory...")
        logger.debug("	{src} => {dest}".format(src=srcPath, dest=dstPath))

        try:
            copy_tree(str(srcPath), str(dstPath))
        except Exception:
            logger.warning("Warning: Problem copying the theme's static files")

        logger.info("Copying course's static directory to the build's static directory...")

        srcPath = self.course.get_static_dir()
        dstPath = self.course.get_build_dir() / 'static'
        logger.debug("	{src} => {dest}".format(src=srcPath, dest=dstPath))
        try:
            copy_tree(str(srcPath), str(dstPath))
        except Exception:
            logger.warning("Warning: Problem copying Course's static directory!")
