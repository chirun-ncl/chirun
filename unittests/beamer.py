from . import ChirunCompilationTest

class BeamerTest(ChirunCompilationTest):
    """
        Tests the beamer document class for prior issues
    """
    source_path = 'beamer'
    compile_args = ['-f', 'test.tex']

    def setUp(self):
        self.tikz_path = self.build_dir / 'images' / 'img-0001.svg'  
    
    def test_sizing(self):
        soup = self.get_soup('index.html')
        img = soup.select('.item-content img')
        imgStyle = img[0]['style'].split(";")
        imgWidth = float(imgStyle[0].split(":")[1][:-2])
        self.assertAlmostEqual(imgWidth, 85.36 ,places=1, msg='The image has a width of 3cm')

