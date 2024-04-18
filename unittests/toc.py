from . import ChirunCompilationTest

class TOCTest(ChirunCompilationTest):
    source_path = 'toc'
    compile_args = ['-f', 'test.tex']

    def test_toc_entries(self):
        """ Check that the right table of contents entries are created.

            Tests https://github.com/chirun-ncl/chirun/issues/223
        """

        soup = self.get_soup('index.html')

        toc = soup.select_one('#sidebar .table-of-contents')
        title_link = toc.li.a
        self.assertEqual(title_link['href'], '#this_is_a_test_docum')
        self.assertEqual(title_link.text.strip(), 'This is a test document')

        section_link = toc.li.ol.li.a
        self.assertEqual(section_link['href'], '#a0000000002')
        self.assertEqual(section_link.text.strip(), '1 A section')
