from . import chirun_version
from . import mkdir_p
from .item import load_item
from . import process
from . import slugify
from .theme import Theme
from . import oembed
from . import plastex
import argparse
import chirun
import copy
import datetime
import hashlib
import json
import logging
import os
from pathlib import Path, PurePath
import shutil
from urllib.parse import urlparse
import yaml
import zipfile


logging.setLoggerClass(logging.Logger)
logger = logging.getLogger('chirun')

class Chirun:

    VERSION = chirun_version.VERSION

    mathjax_url = 'https://cdn.jsdelivr.net/npm/mathjax@4/tex-mml-chtml.js'
    processor_classes = [
        process.SlugCollisionProcess,
        process.LastBuiltProcess,
        process.PDFProcess,
        process.NotebookProcess,
        process.ExpandDocumentProcess,
        process.FlattenStructureProcess,
        process.RenderProcess,
        process.FindHiddenItemsProcess,
    ]

    def __init__(self, args):
        self.args = args
        self.force_relative_build = False

        self.root_dir = self.get_root_dir()
        self.build_dir = (Path(args.build_path) if args.build_path is not None else (self.root_dir / 'build')).resolve()

        self.hidden_paths = []  # A list of directories containing hidden items, filled in by process.FindHiddenItemsProcess.
        self.hidden_files = [Path('MANIFEST_hidden.json')]

        if args.veryverbose:
            args.verbose = True

        if args.verbose:
            if args.veryverbose:
                logger.setLevel(logging.DEBUG)
                logging.basicConfig(format='[%(name)s:%(funcName)s:%(lineno)d] %(message)s')
            else:
                logger.setLevel(logging.INFO)
                logging.basicConfig(format='%(message)s')

        TEXINPUTS = [os.path.dirname(os.path.realpath(chirun.__file__)), '']
        TEXINPUTS += [os.environ.get('TEXINPUTS', '')]
        os.environ['TEXINPUTS'] = ':'.join(TEXINPUTS)

    def get_root_dir(self):
        """
            The path to the course's source directory
        """
        return Path(self.args.dir)

    def get_build_dir(self):
        """
            The path the output will be put in
        """
        return self.build_dir / self.theme.path

    def get_static_dir(self):
        """
            The path to the course's static files source
        """
        return Path(self.config['static_dir'])

    def get_web_root(self):
        """
            The root URL of the course.
        """
        base = self.config.get('base_dir')
        code = self.config.get('code')
        year = self.config.get('year')
        theme_path = self.theme.path

        if 'root_url' not in self.config.keys():
            self.config['root_url'] = '/{base}/'
            if code:
                self.config['root_url'] += '{code}/'
            if len(self.config['themes']) > 1:
                self.config['root_url'] += '{theme}/'

        if not self.args.absolute or self.force_relative_build:
            return str(self.get_build_dir().resolve()) + '/'
        else:
            return self.config.get('root_url').format(base=base, code=code, year=year, theme=theme_path)

    def make_relative_url(self, item, url, output_url=None):
        """
            Make the URL relative to the item's location.

            If the 'absolute' option is turned on, the web root is instead added
            to the beginning of absolute URLs, when required.
        """
        root = self.get_web_root()
        if self.args.absolute:
            if url[:len(root) - 1] != root[1:]:
                url = root + url
            else:
                url = '/' + url
            return url
        else:
            parsed_url = urlparse(url)
            if parsed_url.scheme != '':
                return url

            _url = url

            path = parsed_url.path

            item_url = item.out_file if output_url is None else PurePath(output_url)

            levels = len(item_url.parents) - 1

            if path.startswith(root[1:]):
                path = path[len(root) - 1:]

            path = PurePath(path)
            i = 0
            while i<len(item_url.parts) and i<len(path.parts) and item_url.parts[i] == path.parts[i]:
                i += 1

            levels -= i

            path = PurePath(*path.parts[i:])

            if len(path.parts) == 0:
                return '#'+parsed_url.fragment

            url = str(path)
            if parsed_url.fragment:
                url += '#'+parsed_url.fragment

            if levels > 0:
                return '/'.join((['..'] * levels) + [url])
            else:
                return url

    def default_config(self):
        root_dir = self.get_root_dir()
        config = {
            'locale': 'en',
            'static_dir': root_dir / 'static',
            'build_pdf': True,
            'build_zip': True,
            'num_pdf_runs': 1,
            'year': datetime.datetime.now().year,
            'format_version': 2,
            'mathjax_url': self.mathjax_url,
            'themes': [{
                'title': 'Default',
                'source': 'default',
                'path': '.'
            }],
            'license': None,
        }
        return config

    def get_config_file(self):
        """
            The path to the config file
        """
        if self.args.config_file:
            return Path(self.args.config_file)
        else:
            return self.get_root_dir() / 'config.yml'

    def load_config(self):
        """
            Load the config.

            Extend the default config with the config loaded from the filesystem
        """

        self.config = self.default_config()

        config_file = self.get_config_file()

        logger.debug("Reading config file {}".format(config_file))

        if config_file.exists():
            with open(str(config_file), 'r') as f:
                try:
                    loaded_config = self.loaded_config = yaml.load(f, Loader=yaml.CLoader)
                except AttributeError:
                    loaded_config = self.loaded_config = yaml.load(f, Loader=yaml.Loader)
            self.config.update(loaded_config)

        else:
            if self.args.single_file is None:
                raise Exception(f"The config file {config_file} does not exist.")

        if self.args.single_file:
            self.config.update({
                'build_pdf': self.args.build_pdf,
                'structure': [
                    {
                        'type': 'standalone',
                        'sidebar': True,
                        'topbar': False,
                        'footer': True,
                        'source': self.args.single_file
                    }
                ]
            })

        self.config['args'] = self.args

    def get_hash_salt(self):
        """
            Get a salt string to use when hashing strings.
            The salt should be the same each time the course is built, so that output URLs are consistent.
        """
        if self.args.hash_salt:
            return self.args.hash_salt
        else:
            return self.config.get('hash_salt', '')

    def hash_string(self, text):
        """
            Hash a string, using the course's salt.
        """

        return hashlib.sha256((text + self.get_hash_salt()).encode('utf-8')).hexdigest()

    def get_main_file(self):
        if self.args.single_file:
            return Path(self.args.single_file)
        else:
            return self.get_config_file()

    def theme_directories(self):
        """
            An iterator for paths containing themes

            Tries:
                * The themes_dir path specified in the config
                * The directory 'themes' under the root directory of the course
                * The directory 'themes' in the chirun package
                * The directory 'themes' in the current working directory
        """
        if 'themes_dir' in self.config:
            yield Path(self.config.get('themes_dir'))
        yield self.get_root_dir() / 'themes'
        yield Path(__file__).parent / 'themes'
        yield Path(chirun.__file__).parent / 'themes'
        yield Path('themes')

    def find_theme(self, name):
        """
            Find the source directory for the theme with the given name
        """
        logger.debug("Finding theme {}".format(name))
        for path in self.theme_directories():
            p = path / name
            logger.debug("Trying {}".format(p))
            if p.exists():
                return p

        raise Exception("Couldn't find theme {}".format(name))

    def load_themes(self):
        """
            Load every theme defined in the config
        """
        self.themes = []
        for theme_data in self.config['themes']:
            name = theme_data['source']
            source = self.find_theme(name)
            theme = Theme(self, name, source, theme_data)
            self.themes.append(theme)

    def copy_static_files(self):
        """
            Copy any files in the course's `static` directory to `build_dir/static`
        """
        logger.debug("Copying course's static directory to the build's static directory...")

        srcPath = self.get_static_dir()
        dstPath = self.get_build_dir() / 'static'

        if srcPath.is_dir():
            logger.debug("    {src} => {dest}".format(src=srcPath, dest=dstPath))

            try:
                shutil.copytree(str(srcPath), str(dstPath), dirs_exist_ok=True)
            except Exception:
                logger.warning("Warning: Problem copying Course's static directory!")

    def load_structure(self):
        """
            Load all the items defined in the config
        """
        logger.debug('Loading course structure')
        self.structure = [load_item(self, obj) for obj in self.config.get('structure', [])]

        # Ensure an item exists in the course structure to produce an index page.
        if not any(item.is_index for item in self.structure):
            index = {'type': 'introduction'}
            self.structure.insert(0, load_item(self, index))

    def process(self):
        """
            Process the course.
            Each process visits all the items in the course structure and builds a different format.
        """
        logger.debug("Starting processing")

        processors = [p(self) for p in self.processor_classes]
        for processor in processors:
            logger.info("Process: " + processor.name)
            for n in range(processor.num_runs):
                if processor.num_runs > 1:
                    logger.info("Run {}/{}".format(n + 1, processor.num_runs))
                processor.process(run_number=n)

        logger.debug('Finished processing course items')

    def optimize(self):
        pass

    def get_zipfile_name(self):
        if not self.config['build_zip']:
            return None

        return Path(slugify(self.config.get('title','chirun'))).with_suffix('.zip')

    def package_zip(self):
        """
            Compress the package's output into a zip file.
        """

        zipfile_name = self.get_zipfile_name()

        if zipfile_name is None:
            return

        zipfile_path = self.build_dir / zipfile_name

        if zipfile_path.exists():
            zipfile_path.unlink()

        with zipfile.ZipFile(zipfile_path, mode='w') as zf:
            for d, dirs, files in os.walk(str(self.build_dir)):
                if any(Path(d).is_relative_to(self.build_dir / p) for p in self.hidden_paths):
                    continue
                for f in files:
                    p = self.build_dir.parent / d / f
                    fname = p.relative_to(self.build_dir)
                    if fname in self.hidden_files:
                        continue
                    if fname == zipfile_name:
                        continue
                    zf.write(p, fname)


    def temp_path(self, subpath=None):
        """
            Construct a temporary directory to do work in.
            Deleted at the end, in Chirun.cleanup.
        """
        path = Path('tmp') / self.theme.path

        if subpath:
            path = path / subpath

        mkdir_p(path)
        return path

    def cleanup(self):
        """
            Remove temporary files created during the build process
        """
        logger.info("Cleaning up temporary files")

        try:
            shutil.rmtree('tmp')
        except OSError:
            pass

    def make_directories(self):
        """
            Make the output directory
        """
        logger.debug("Creating build directory...")
        mkdir_p(self.get_build_dir())
        mkdir_p(self.get_build_dir() / 'static')

    def save_manifest(self):
        """
            Write out a manifest similar to config.yml, but
            including possible changes to the structure introduced
            by item types that dynamically create further content
            items.
        """

        manifest = copy.deepcopy(self.config)

        def remove_hidden(items):
            items = [item for item in items if not item['is_hidden']]
            for item in items:
                if 'content' in item:
                    item['content'] = remove_hidden(item['content'])
            return items

        del manifest['args']
        del manifest['static_dir']

        manifest.update({
            'zipfile': str(self.get_zipfile_name()),
            'structure': [item.content_tree() for item in self.structure],
        })

        hidden_manifest = copy.deepcopy(manifest)

        manifest.update({
            'structure': remove_hidden(manifest['structure']),
        })

        manifest_path = self.build_dir / 'MANIFEST.yml'

        with open(manifest_path, 'w') as f:
            yaml.dump(manifest, f)

        with open(manifest_path.with_suffix('.json'), 'w') as f:
            json.dump(manifest, f)

        with open(self.build_dir / 'MANIFEST_hidden.json', 'w') as f:
            json.dump(hidden_manifest, f)


    def build_with_theme(self, theme):
        """
            Build the course using the given theme
        """
        self.theme = theme

        logger.debug("""
The static directory is: {static_dir}
The build directory is: {build_dir}
The web root directory is: {web_root}
""".format(
            static_dir=self.get_static_dir(),
            build_dir=self.get_build_dir(),
            web_root=self.get_web_root(),
        ))

        self.make_directories()
        theme.copy_static_files()
        self.copy_static_files()
        self.process()
        self.optimize()

    def build_theme_redirect(self):
        """
            When the output HTML files aren't at the top of the output directory,
            because there's more than one theme, make an index.html
            redirecting to the first theme.
        """

        path = self.build_dir / 'index.html'
        with open(path, 'w') as f:
            f.write(
                f'''<!doctype html>
<html>
    <head>
        <meta http-equiv="refresh" content="0; url={self.themes[0].path}/index.html">
    </head>
    <body>
        <ul>''')
            for theme in self.themes:
                f.write(f'''<li><a href="{theme.path}/index.html">{theme.title}</a></li>''')
            f.write('''</ul></body></html>''')

    def build(self):
        print("Running chirun for directory {}".format(self.get_root_dir().resolve()))

        oembed.load_cache()

        self.load_config()

        self.load_themes()

        self.load_structure()

        for theme in self.themes:
            self.build_with_theme(theme)

        if len(self.themes) > 1:
            self.build_theme_redirect()

        self.save_manifest()

        self.package_zip()

        self.cleanup()

        oembed.save_cache()


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', dest='build_path', help='Set a directory to put build files in.\
            Defaults to a directory named \'build\' in the current directory.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Verbose output.')
    parser.add_argument('-vv', dest='veryverbose', action='store_true', help='Very verbose output.')
    parser.add_argument('-d', dest='cleanup_all', action='store_true', help='Delete auxiliary files.')
    parser.add_argument('-a', dest='absolute', action='store_true', help='Output using absolute file paths, \
            relative to the configured root_url.')
    parser.add_argument('--config', dest='config_file', help='Path to a config file. Defaults to \'config.yml\'.')
    parser.add_argument('-l', dest='local-deprecated', action='store_true', help='Deprecated and has no effect.\
            This option will be removed in a future version.')
    parser.add_argument('-z', dest='lazy-deprecated', action='store_true', help='Deprecated and has no effect.\
            This option will be removed in a future version.')
    parser.add_argument('dir', help='Path to a chirun compatible source directory.\
            Defaults to the current directory.', default='.', nargs='?')
    parser.add_argument('-f', dest='single_file', help='The path to a single file to build')
    parser.add_argument('--no-pdf', dest='build_pdf', action='store_false', help='Don\'t build PDF files')
    parser.add_argument('--hash-salt', dest='hash_salt', default='',
                        help='Salt string for hashing paths to hidden items')
    parser.set_defaults(build_pdf=True)
    return parser

def main():
    args = arg_parser().parse_args()

    extensions = [
        plastex.PlastexRunner,
    ]

    class Builder(Chirun, *extensions):
        pass

    mc = Builder(args)
    mc.build()

    print("Output written to {}".format(mc.build_dir.resolve()))


if __name__ == "__main__":
    main()
