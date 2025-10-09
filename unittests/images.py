from . import ChirunCompilationTest

class LaTeXImageTest(ChirunCompilationTest):
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
        self.assertTrue(img[0]['src'].startswith('images/img-0001.jpg'), msg='The jpg is embedded as an <img> tag.')
        self.assertTrue(img[1]['src'].startswith('images/img-0002.png'), msg='The png is embedded as an <img> tag.')
    
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

class MarkdownImageTest(ChirunCompilationTest):
    """
        Tests the upload of many different image types
    """
    source_path = 'images'
    compile_args = ['-f', 'test.md', '--no-pdf']

    def test_image_urls(self):
        """ Check that the ``src`` URLs for images are correct.

            Tests #234
        """

        soup = self.get_soup('index.html')

        images = soup.select('.item-content img')

        sources = ['images/drawing.png', 'images/drawing.png', 'images/drawing-0000.png', 'images/drawing-0000.png', 'images/Uniform_tiling_circle_packings.png', 'images/Penrose_tiling_at_Oxford_Mathematical_Institute_small.jpg', 'images/diagram.svg']
        alt = ['drawing 1 markdown', 'drawing 1 tag', 'drawing 2 markdown', 'drawing 2 tag', 'Tilings', 'Penrose', 'Diagram']
        for i, img in enumerate(images):
            self.assertTrue(img['src'].startswith(sources[i]))
            self.assertTrue((self.build_dir / sources[i]).exists())
