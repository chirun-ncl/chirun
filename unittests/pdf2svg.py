from . import ChirunCompilationTest

class PDF2SVGTest(ChirunCompilationTest):
    """
        A single LaTeX document which includes a graphic in PDF format.

        Tests issue #4
    """
    source_path = 'pdf2svg'
    compile_args = ['-f', 'test.tex']

    def setUp(self):
        self.pdf_image_path = self.build_dir / 'images' / 'img-0001.svg'
        self.eps_image_path = self.build_dir / 'images' / 'img-0002.svg'

    def test_image_exists(self):
        self.assertTrue(self.pdf_image_path.exists(), msg=f'The PDF image is converted to SVG at {self.pdf_image_path}')
        self.assertTrue(self.eps_image_path.exists(), msg=f'The EPS image is converted to SVG at {self.eps_image_path}')

    def test_image_reference(self):
        soup = self.get_soup('index.html')
        img = soup.select('.item-content img')
        self.assertEqual(img[0]['src'], 'images/img-0001.svg', msg='The PDF image is embedded as an <img> tag.')
        self.assertEqual(img[1]['src'], 'images/img-0002.svg', msg='The EPS image is embedded as an <img> tag.')
