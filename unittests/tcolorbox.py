from . import ChirunCompilationTest

class TColorBoxTest(ChirunCompilationTest):
    source_path = 'tcolorbox'
    compile_args = ['-f', 'test.tex']

    def test_box_color(self):
        r""" Test that custom colours are reflected in the background of the box.
        """
        soup = self.get_soup('index.html')

        box = soup.find(name='div',style='background-color:#00FF00; border-color:#1E32B4')
        self.assertIsNotNone(box)

