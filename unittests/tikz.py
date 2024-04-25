from . import ChirunCompilationTest

class TikzTest(ChirunCompilationTest):
    """
        Compile a single LaTeX document containing a tikz diagram including simple draw and node commands.

        Tests https://github.com/chirun-ncl/chirun/issues/44 and https://github.com/chirun-ncl/chirun/issues/5
    """
    source_path = 'tikz'
    compile_args = ['-f', 'test.tex']

    def setUp(self):
        self.image_path = self.build_dir / 'images' / 'img-0001.svg'

    def test_compilation_succeeded(self):
        self.assertEqual(self.compilation.returncode, 0)

    def test_image_exists(self):
        self.assertTrue(self.image_path.exists(), msg=f'The image is present at {self.image_path}')

    def test_alttext_exists(self):
        soup = self.get_soup('index.html')
        img = soup.select('.item-content img')
        self.assertEqual(img[0]['alt'], 'A box with an arrow from lower left to upper right, and a node midway along the base', msg='The tikz image has alt text.')


