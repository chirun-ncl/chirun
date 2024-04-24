from . import ChirunCompilationTest

class ImageTest(ChirunCompilationTest):
    """
        Tests that the picture environment does not break maths
    """
    source_path = 'picture'
    compile_args = ['-f', 'test.tex']

    def setUp(self):
        self.img_path = self.build_dir / 'images' / 'img-0001.svg'
        
    def test_jpg_exists(self):
        self.assertTrue(self.img_path.exists(), msg=f'The image is stored as an svg at {self.img_path}')
        
