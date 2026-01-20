from . import ChirunCompilationTest

class TColorBoxTest(ChirunCompilationTest):
    source_path = 'tcolorbox'
    compile_args = ['-f', 'test.tex']

    def test_box_color(self):
        r""" Test that custom colours are reflected in the background of the box.
        """
        soup = self.get_soup('index.html')

        box = soup.find(name='div',class_='tcolorbox')
        self.assertIsNotNone(box)
        self.assertEqual(box['style'], '--colback:#00FF00; --colupper:#0000FF; --collower:#0000FF; --colframe:#1E32B4')

