from . import ChirunCompilationTest

class RaiseboxTest(ChirunCompilationTest):
    source_path = 'raisebox'

    compile_args = ['-f', 'test.tex']

    def test_raisebox(self):
        """ Check that ``\raisebox`` is rendered in HTML as an element with changed ``vertical-align``.

            Tests https://github.com/chirun-ncl/chirun/issues/136
        """
        soup = self.get_soup('index.html')

        raiseboxes = soup.select('.raisebox')

        self.assertEqual(len(raiseboxes), 2)

        self.assertEqual(raiseboxes[0]['style'], 'vertical-align: 5.0pt')
        self.assertEqual(raiseboxes[1]['style'], 'vertical-align: -11.0pt')
