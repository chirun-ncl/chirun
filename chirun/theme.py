import logging
from pathlib import Path
import os
import shutil

logger = logging.getLogger(__name__)


class Theme(object):
    def __init__(self, course, name, source, theme_data):
        self.course = course
        self.hidden = False
        self.name = name
        self.source = source
        keys = ('title', 'path', 'hidden')
        for key in keys:
            if key in theme_data:
                setattr(self, key, theme_data[key])

    def __str__(self):
        return '{}'.format(self.title)

    def __repr__(self):
        return '<chirun.theme.Theme: {}>'.format(self.title)

    @property
    def template_path(self):
        return self.source / 'templates'

    @property
    def translations_path(self):
        return (self.source / 'translations' / self.course.config['locale']).with_suffix('.mo')

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

        logger.debug("Copying theme's static directory to the build's static directory...")
        logger.debug("    {src} => {dest}".format(src=srcPath, dest=dstPath))

        try:
            shutil.copytree(str(srcPath), str(dstPath), dirs_exist_ok=True)
        except Exception:
            logger.warning("Warning: Problem copying the theme's static files")

        js_translation = (self.source / 'translations' / self.course.config['locale']).with_suffix('.mjs')
        if js_translation.exists():
            shutil.copyfile(js_translation, dstPath / 'translations.js')
