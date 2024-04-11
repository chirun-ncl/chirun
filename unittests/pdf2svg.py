from . import ChirunCompilationTest

class PDF2SVGTest(ChirunCompilationTest):
    source_path = 'pdf2svg'
    compile_args = ['-f', 'test.tex']

    def setUp(self):
        self.image_path = self.build_dir / 'images' / 'img-0001.svg'

    def test_image_exists(self):
        self.assertTrue(self.image_path.exists(), msg=f'The image is converted to SVG at {self.image_path}')

    def test_image_reference(self):
        soup = self.get_soup('index.html')
        img = soup.select('.item-content img')
        self.assertEqual(img[0]['src'], 'images/img-0001.svg', msg='The image is embedded as an <img> tag.')
