from . import ChirunCompilationTest

class DoubleDocumentTest(ChirunCompilationTest):
    source_path = 'double_document'
    compile_args = ['-f', 'test.tex', '--no-pdf']

    def test_slash(self):
        """ Check that plasTeX can cope with a TeX file containing more than one ``document`` environment.

            Tests https://github.com/chirun-ncl/chirun/issues/214
        """
        soup = self.get_soup('index.html')

        self.assertEqual(soup.select_one('.item-content').text.strip(),'First document')
