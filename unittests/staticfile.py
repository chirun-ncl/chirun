from . import ChirunCompilationTest
import pypdf

class StaticFileTest(ChirunCompilationTest):
    """ Check that static files are copied and relative links are produced in the HTML output.

        Tests https://github.com/chirun-ncl/chirun/issues/42
    """
    source_path = 'staticfile'

    def test_static_file_copies(self):
        self.assertTrue((self.build_dir / 'static' / 'text.txt').exists())
        self.assertTrue((self.build_dir / 'static' / 'test.tex').exists())
        self.assertTrue((self.build_dir / 'static' / 'other.txt').exists())

    def test_latex_links(self):
        soup = self.get_soup('latex_document_linki/index.html')

        links = soup.select('.item-content a')
        self.assertEqual(links[0]['href'], '../static/text.txt')
        self.assertEqual(links[1]['href'], '../static/test.tex')

    def test_markdown_links(self):
        soup = self.get_soup('markdown_document_li/index.html')

        links = soup.select('.item-content a')
        self.assertEqual(links[0]['href'], '../static/text.txt')
        self.assertEqual(links[1]['href'], '../static/test.tex')

    def test_markdown_pdf_links(self):
        """ Check that relative links in the PDF produced from markdown source are really relative.

            Tests #82
        """

        pdf = self.build_dir / 'markdown_document_li' / 'markdown_document_li.pdf'

        reader = pypdf.PdfReader(str(pdf))
        
        links = []
        for page in reader.pages:
            for annot in page['/Annots']:
                if annot['/Subtype'] != '/Link':
                    continue
                links.append(annot['/A']['/URI'])

        self.assertIn('../static/text.txt', links)
        self.assertIn('../static/test.tex', links)
        self.assertIn('https://www.chirun.org.uk/', links)

    def test_part_markdown_pdf_links(self):
        """ Check that relative links in the PDF produced from markdown source in a subdirectory are really relative.

            Tests #82
        """

        pdf = self.build_dir / 'a_part' / 'markdown_document_in' / 'markdown_document_in.pdf'

        reader = pypdf.PdfReader(str(pdf))
        
        links = []
        for page in reader.pages:
            for annot in page['/Annots']:
                if annot['/Subtype'] != '/Link':
                    continue
                links.append(annot['/A']['/URI'])

        self.assertIn('../../static/text.txt', links)
        self.assertIn('../../static/test.tex', links)
        self.assertIn('https://www.chirun.org.uk/', links)

    def test_manifest(self):
        manifest = self.get_manifest()

        self.assertEqual(manifest['structure'][3]['content'][0]['url'], 'static/text.txt')

    def test_url_item(self):
        """ Test that the index page for a p art correctly links to a static file.

            Tests https://github.com/chirun-ncl/chirun/issues/54
        """

        soup = self.get_soup('a_part/index.html')

        self.assertEqual(soup.select_one('.chirun-structure .contents a')['href'], '../static/text.txt')
