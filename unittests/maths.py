from . import ChirunCompilationTest

class MathsTest(ChirunCompilationTest):
    source_path = 'maths'
    compile_args = ['-f', 'test.tex']

    def test_adjacent_inline_maths(self):
        """ Check that two passages of inline math delimited by dollar signs are rendered OK.

            Tests https://github.com/chirun-ncl/chirun/issues/50
        """

        soup = self.get_soup('index.html')

        self.assertIn(r'\(x\)\(y\)', soup.select('.item-content p')[0].text)
