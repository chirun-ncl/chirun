from bs4 import BeautifulSoup
import json
import unittest
from pathlib import Path
import shutil
import subprocess
import tempfile

class ChirunCompilationTest(unittest.TestCase):
    """ A unit test which compiles a Chirun package.
        The files in the ``source_path`` are copied to a temporary directory before being compiled.
    """

    compile_args = []

    @property
    def source_path(self):
        """ The path to the test's source files.
        """
        raise NotImplementedError

    @classmethod
    def setUpClass(cls):
        source_path = Path(__file__).parent / cls.source_path
        cls.tmpdir = tempfile.TemporaryDirectory()
        shutil.copytree(source_path, cls.tmpdir.name, dirs_exist_ok=True)
        cls.root = Path(cls.tmpdir.name)
        cls.compilation = subprocess.run(['chirun']+cls.compile_args, cwd=cls.root, capture_output=True, encoding='utf8')
        cls.build_dir = cls.root / 'build'

    @classmethod
    def tearDownClass(cls):
        cls.tmpdir.cleanup()

    def get_soup(self, path):
        """
            Get a BeautifulSoup instance for the given HTML file in the build directory.
        """

        with open(self.build_dir / path) as fp:
            return BeautifulSoup(fp, 'html.parser')

    def get_manifest(self):
        with open(self.build_dir / 'MANIFEST.json') as fp:
            return json.load(fp)

from .basic import *
from .pdf2svg import *

if __name__ == '__main__':
    unittest.main()
