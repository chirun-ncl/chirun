from . import ChirunCompilationTest

class ImageTest(ChirunCompilationTest):
    """
        Tests the upload of many different image types
    """
    source_path = 'images'
    compile_args = ['-f', 'test.tex']

    def setUp(self):
        self.jpg_path = self.build_dir / 'images' / 'img-0001.jpg'
        self.png_path = self.build_dir / 'images' / 'img-0002.png'
        
    def test_compilation_succeeded(self):
        self.assertEqual(self.compilation.returncode, 0)

    def test_jpg_exists(self):
        self.assertTrue(self.jpg_path.exists(), msg=f'The image is stored as a JPG at {self.jpg_path}')

    def test_png_exists(self):
        self.assertTrue(self.png_path.exists(), msg=f'The image is stored as a PNG at {self.png_path}')

    def test_image_reference(self):
        soup = self.get_soup('index.html')
        img = soup.select('.item-content img')
        self.assertEqual(img[0]['src'], 'images/img-0001.jpg', msg='The jpg is embedded as an <img> tag.')
        self.assertEqual(img[1]['src'], 'images/img-0002.png', msg='The png is embedded as an <img> tag.')
    
    def test_alt_text(self):
        soup = self.get_soup('index.html')
        img = soup.select('.item-content img')
        self.assertEqual(img[0]['alt'], 'Penrose tiling with curved metal accents', msg='The jpg has alt text as defined with alttext.')
        
