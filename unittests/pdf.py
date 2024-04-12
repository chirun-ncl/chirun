from . import ChirunCompilationTest

class PDFTest(ChirunCompilationTest):
    source_path = 'pdf'

    def test_per_item_pdf(self):
        """ Check that you can prevent a single item from having a PDF built.

            Tests https://github.com/chirun-ncl/chirun/issues/96
        """

        self.assertTrue((self.build_dir / 'latex_document_1' / 'latex_document_1.pdf').exists())
        self.assertFalse((self.build_dir / 'latex_document_2' / 'latex_document_2.pdf').exists())
