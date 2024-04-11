from . import ChirunCompilationTest
from pathlib import Path

class TikzTest(ChirunCompilationTest):
    """
        Compile a single LaTeX document containing a tikz diagram including simple draw and node commands.
    """
    source_path = 'tikz'
    compile_args = ['-f', 'test.tex']

    def setUp(self):
        self.image_path = self.build_dir / 'images' / 'img-0001.svg'

    def test_compilation_succeeded(self):
        self.assertEqual(self.compilation.returncode, 0)

    def test_image_exists(self):
        self.assertTrue(self.image_path.exists(), msg=f'The image is present at {self.image_path}')


