from . import ChirunCompilationTest
from PIL import Image

class BeamerTest(ChirunCompilationTest):
    """
        Tests the beamer document class for prior issues
    """
    source_path = 'beamer'
    compile_args = ['-f', 'test.tex']

    def setUp(self):
        self.pdf_path = self.build_dir / 'images' / 'img-0001.svg'  
        self.tikz_path = self.build_dir / 'images' / 'img-0002.svg'  
        self.png_path = self.build_dir / 'images' / 'img-0001.png'  
    
    def test_sizing(self):
        pdfViewbox = 'viewBox="0 0 315.01462 356.974953"'
        tikzViewbox = 'viewBox="0 0 87 58"'
        pngWidth = 400
        with open(self.pdf_path) as pdfSvg:
            self.assertIn(pdfViewbox, pdfSvg.read())
        with open(self.tikz_path) as tikzSvg:
            self.assertIn(tikzViewbox, tikzSvg.read())
        with Image.open(self.png_path) as pngPng:
            self.assertEqual(pngWidth, pngPng.width)

