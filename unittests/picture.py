from . import ChirunCompilationTest

class ImageTest(ChirunCompilationTest):
    """
        Tests that the picture environment does not break maths

        Tests https://github.com/chirun-ncl/chirun/issues/126
    """
    source_path = 'picture'
    compile_args = ['-f', 'test.tex']

    def setUp(self):
        self.img_path = self.build_dir / 'images' / 'img-0001.svg'
        
    def test_jpg_exists(self):
        self.assertTrue(self.img_path.exists(), msg=f'The image is stored as an svg at {self.img_path}')
        

    def test_image_reference(self):
        soup = self.get_soup('index.html')
        img = soup.select('.item-content img')
        #A break of issue #126 will have an 'object' and raw text where the 'image' would be
        self.assertTrue(img[0]['src'].startswith('images/img-0001.svg'), msg='The maths is embedded as an <img> tag.')
