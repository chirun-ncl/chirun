from . import ChirunCompilationTest

class MathsTest(ChirunCompilationTest):
    source_path = 'maths'

    def test_adjacent_inline_maths(self):
        """ Check that two passages of inline math delimited by dollar signs are rendered OK.

            Tests https://github.com/chirun-ncl/chirun/issues/50
        """

        soup = self.get_soup('latex_maths/index.html')

        self.assertIn(r'\(x\)\(y\)', soup.select('.item-content p')[0].text)

    def test_markdown_display_without_newline(self):
        """ Test that backslashes in display mode maths on the same line as other text work without escaping.

            Tests https://github.com/chirun-ncl/chirun/issues/60
        """

        soup = self.get_soup('markdown_maths/index.html')

        display_maths = soup.select_one('.item-content p script[type="math/tex; mode=display"]')
        self.assertEqual(display_maths.text.strip(), r'\frac{1}{2}')
