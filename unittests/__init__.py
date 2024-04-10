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

class BasicTest(ChirunCompilationTest):
    source_path = 'basic'

    """
        Compile a single LaTeX document with almost nothing in it, and check that the general layout is correct.
    """

    def test_compilation_succeeded(self):
        self.assertEqual(self.compilation.returncode, 0)

    def test_chapter_dir_exists(self):
        document_dir = self.build_dir / 'basic_document'
        self.assertTrue(document_dir.exists(), msg=f'{document_dir} exists')

    def test_links(self):
        intro = self.get_soup('index.html')

        item_links = intro.select('.chirun-structure .item .contents > li > a')
        self.assertEqual(len(item_links), 1, msg="There is only one item")
        item_link = item_links[0]
        self.assertEqual(item_link['href'], 'basic_document/index.html', msg="The link to the item is relative")

    def test_structure(self):
        manifest = self.get_manifest()

        self.assertEqual(len(manifest['structure']), 2, msg="There are two items in the structure.")
        self.assertEqual([x['type'] for x in manifest['structure']], ['introduction', 'chapter'], msg="There is an introduction and a chapter.")

class BasicStandaloneTest(ChirunCompilationTest):
    """
        Compile a single LaTeX document in standalone mode.
    """

    source_path = 'basic'
    compile_args = ['-f','test.tex']

    def test_standalone_compilation(self):
        self.assertEqual(self.compilation.returncode, 0)

    def test_index_exists(self):
        self.assertTrue((self.build_dir / 'index.html').exists())

    def test_structure(self):
        manifest = self.get_manifest()

        self.assertEqual(len(manifest['structure']), 1, msg="There is only one item in the structure.")

if __name__ == '__main__':
    unittest.main()
