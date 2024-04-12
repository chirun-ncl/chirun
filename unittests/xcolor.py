from . import ChirunCompilationTest

class XColorTest(ChirunCompilationTest):
    source_path = 'xcolor'
    compile_args = ['-f', 'test.tex']

    def test_text_color(self):
        """ Test that the \color command changes the color of text.
            
            Tests https://github.com/chirun-ncl/chirun/issues/36
        """
        soup = self.get_soup('index.html')

        green = soup.find(name='span', style='color:#00FF00')
        self.assertIsNotNone(green)
        self.assertEqual(green.text.strip(),'Green text.')
