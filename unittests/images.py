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
        self.assertTrue(self.jpg_path.exists(), msg=f'The image is stored as an JPG at {self.jpg_path}')

    def test_png_exists(self):
        self.assertTrue(self.png_path.exists(), msg=f'The image is stored as an PNG at {self.png_path}')

    def test_image_reference(self):
        soup = self.get_soup('index.html')
        img = soup.select('.item-content img')
        self.assertEqual(img[0]['src'], 'images/img-0001.jpg', msg='The jpg is embedded as an <img> tag.')
        self.assertEqual(img[1]['src'], 'images/img-0002.png', msg='The png is embedded as an <img> tag.')
        self.assertEqual(img[2]['src'], 'images/img-0003.png', msg='The eps is converted to a png and embedded as an <img> tag.')
    
    def test_sizing(self):
        soup = self.get_soup('index.html')
        img = soup.select('.item-content img')
        jpgStyle = img[0]['style'].split(";")
        jpgWidth = float(jpgStyle[0].split(":")[1][:-2])
        self.assertAlmostEqual(jpgWidth, 375.8,places=1, msg='The jpg has a width of 375.8pt, 80% of plastex\'s text width') #plastex \textwidth is 469.755pt
        pngStyle = img[1]['style'].split(";")
        pngWidth = float(pngStyle[0].split(":")[1][:-2])
        pngHeight = float(pngStyle[1].split(":")[1][:-2])
        self.assertAlmostEqual(pngWidth, 2400 ,places=0, msg='The png has a width of 2400px, 2* its base width')
        self.assertAlmostEqual(pngHeight, 2802 ,places=0, msg='The png has a height of 2802px, 2* its base height')

