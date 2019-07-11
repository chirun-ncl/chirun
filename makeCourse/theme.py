import logging
from distutils.dir_util import copy_tree

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
        return self.course.get_themes_dir() / self.source

    @property
    def alt_themes_yaml(self):
        return [t.yaml for t in self.course.themes if not (t.hidden or t == self)]

    @property
    def yaml(self):
        return {
            'title': self.title,
            'source': self.source,
            'path': self.path,
            'hidden': self.hidden,
        }

    def copy_static_files(self):
        srcPath = self.source_path / 'static'
        dstPath = self.course.get_build_dir() / 'static'

        logger.info("Copying Theme's static directory to the build's static directory...")
        logger.info("	{src} => {dest}".format(src=srcPath, dest=dstPath))

        try:
            copy_tree(str(srcPath), str(dstPath))
        except Exception:
            logger.warning("Warning: Problem copying the theme's static files")
            logger.warning(str(e))

        logger.info("Copying course's static directory to the build's static directory...")

        srcPath = self.course.get_static_dir()
        dstPath = self.course.get_build_dir() / 'static'
        logger.info("	{src} => {dest}".format(src=srcPath, dest=dstPath))
        try:
            copy_tree(str(srcPath), str(dstPath))
        except Exception:
            logger.warning("Warning: Problem copying Course's static directory!")

    def build(self):
        course = self.course

        course.setup_build_for_theme(self)

        logger.debug("""The themes directory is: {themes_dir}
The static directory is: {static_dir}
The build directory is: {build_dir}
The web root directory is: {web_root}
The local root directory is: {local_root}""".format(
            themes_dir=course.get_themes_dir(),
            static_dir=course.get_static_dir(),
            build_dir=course.get_build_dir(),
            web_root=course.get_web_root(),
            local_root=course.get_local_root()
        ))

        course.make_directories()
        self.copy_static_files()
        course.process()
