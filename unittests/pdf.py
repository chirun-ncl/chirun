from . import ChirunCompilationTest

class PDFTest(ChirunCompilationTest):
    source_path = 'pdf'

    def test_per_item_pdf(self):
        """ Check that you can prevent a single item from having a PDF built.

            Tests https://github.com/chirun-ncl/chirun/issues/96
        """

        self.assertTrue((self.build_dir / 'latex_document_1' / 'latex_document_1.pdf').exists())
        self.assertFalse((self.build_dir / 'latex_document_2' / 'latex_document_2.pdf').exists())
        self.assertTrue((self.build_dir / 'a_test_document' / 'a_test_document.pdf').exists())
        self.assertTrue((self.build_dir / 'manually_set_title' / 'manually_set_title.pdf').exists())

class StandalonePDFLinkTest(ChirunCompilationTest):
    source_path = 'pdf'
    compile_args = ['-f', 'test.tex']

    def test_pdf_link(self):
        """ Check that the link to the PDF is correct.

            Tests https://github.com/chirun-ncl/chirun/issues/222
        """

        soup = self.get_soup('index.html')

        self.assertTrue((self.build_dir / 'test.pdf').exists())

        pdf_link = soup.select_one('a[rel="alternate"][type="application/pdf"]')
        self.assertEqual(pdf_link['href'], 'test.pdf')
