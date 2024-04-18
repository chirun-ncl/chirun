from . import ChirunCompilationTest

class HyperrefTest(ChirunCompilationTest):
    source_path = 'hyperref'

    compile_args = ['-f', 'test.tex', '--no-pdf']

    def test_html_only_link(self):
        """ Check that a link and label which are only present when compiling with plasTeX are correctly rendered.

            Tests https://github.com/chirun-ncl/chirun/issues/228
        """

        soup = self.get_soup('index.html')

        expect_links = [
            ('numbered', 'numbered section'),
            ('not-numbered', 'not numbered section'),
            ('only-html', 'HTML-only section'),
        ]

        links = soup.select('.item-content a')

        for i, (id_, text) in enumerate(expect_links):
            a = links[i]
            self.assertEqual(a['href'], '#'+id_)
            self.assertEqual(a.text.strip(), text)
            self.assertIsNotNone(soup.find(id=id_))
