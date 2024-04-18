from bs4 import BeautifulSoup
import functools
import json
import unittest
from pathlib import Path
import os
import shutil
import subprocess
import tempfile

class ChirunCompilationTest(unittest.TestCase):
    """ A unit test which compiles a Chirun package.
        The files in the ``source_path`` are copied to a temporary directory before being compiled.
        Run with the environment variable ``KEEP_TEST_OUTPUT=1`` to preserve the contents of the temporary directory, under ``unittests/_kept``
    """

    compile_args = []

    source_path = None

    show_stdout = False # Show the contents of STDOUT after compilation?
    show_stderr = True  # Show the contents of STDERR after compilation?

    @classmethod
    def setUpClass(cls):
        source_path = Path(__file__).parent / cls.source_path
        cls.tmpdir = tempfile.TemporaryDirectory()
        shutil.copytree(source_path, cls.tmpdir.name, dirs_exist_ok=True)
        cls.root = Path(cls.tmpdir.name)

        cls.compile(cls.compile_args)
        cls.check_compilation_returncode()
        cls.build_dir = cls.root / 'build'

    @classmethod
    def compile(cls, compile_args):
        cls.compilation = subprocess.run(['chirun']+compile_args, cwd=cls.root, capture_output=True, encoding='utf8')
        if cls.compilation.stdout.strip() and cls.show_stdout:
            print("STDOUT output:")
            print(cls.compilation.stdout)
        if cls.compilation.stderr.strip() and cls.show_stderr:
            print("STDERR output:")
            print(cls.compilation.stderr)

    @classmethod
    def check_compilation_returncode(cls):
        assert cls.compilation.returncode == 0, "Compilation failed"

    @classmethod
    def tearDownClass(cls):
        if os.environ.get('KEEP_TEST_OUTPUT') == '1':
            keep_dir = Path(__file__).parent / '_kept' / (Path(cls.source_path).name)

            keep_dir.mkdir(exist_ok=True, parents=True)

            if keep_dir.exists():
                shutil.rmtree(keep_dir, ignore_errors=True)

            shutil.copytree(cls.tmpdir.name, keep_dir)

            log_dir = keep_dir / 'logs'
            log_dir.mkdir(exist_ok=True)

            with open(log_dir / 'stdout.log', 'w') as f:
                f.write(cls.compilation.stdout)

            with open(log_dir / 'stderr.log', 'w') as f:
                f.write(cls.compilation.stderr)

            print(f"\nTest files have been kept at {keep_dir}\n")

        cls.tmpdir.cleanup()

    def get_soup(self, path):
        """
            Get a BeautifulSoup instance for the given HTML file in the build directory.
        """

        with open(self.build_dir / path) as fp:
            return BeautifulSoup(fp, 'html.parser')

    @functools.cache
    def get_manifest(self):
        with open(self.build_dir / 'MANIFEST.json') as fp:
            return json.load(fp)

class ExpectCrashTest(ChirunCompilationTest):
    """ A test case which expects Chirun to quit with an error.
    """

    show_stderr = False
    @classmethod
    def check_compilation_returncode(cls):
        pass

from .basic import *
from .bibtex import *
from .double_document import *
from .ifplastex import *
from .images import *
from .latex_crash import *
from .latex_environments import *
from .maths import *
from .missing_source import *
from .notebook import *
from .pdf import *
from .pdf2svg import *
from .placeins import *
from .raisebox import *
from .runnable_code import *
from .slash import *
from .slides import *
from .splitlevel import *
from .staticfile import *
from .structure import *
from .theme_customisation import *
from .tikz import *
from .verbatim import *
from .xcolor import *

if __name__ == '__main__':
    unittest.main()
