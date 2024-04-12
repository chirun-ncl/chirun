from . import ChirunCompilationTest

class StaticFileTest(ChirunCompilationTest):
    """ Check that static files are copied and relative links are produced in the HTML output.

        Tests https://github.com/chirun-ncl/chirun/issues/42
    """
    source_path = 'staticfile'

    def test_static_file_copies(self):
        self.assertTrue((self.build_dir / 'static' / 'text.txt').exists())
        self.assertTrue((self.build_dir / 'static' / 'test.tex').exists())
        self.assertTrue((self.build_dir / 'static' / 'other.txt').exists())

    def test_links(self):
        soup = self.get_soup('document_linking_to_/index.html')

        links = soup.select('.item-content a')
        self.assertEqual(links[0]['href'], '../static/text.txt')
        self.assertEqual(links[1]['href'], '../static/test.tex')
