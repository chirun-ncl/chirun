from . import ChirunCompilationTest
import pypdf

class IfplastexTest(ChirunCompilationTest):
    source_path = 'ifplastex'
    compile_args = ['-f','test.tex']

    def test_ifplastex(self):
        r""" 
            Test that the ``\ifplastex`` and ``\ifpdflatex`` commands are defined and work as expected.

            Tests https://github.com/chirun-ncl/chirun/issues/124
        """

        with open(self.build_dir / 'index.html') as f:
            text = f.read()

        self.assertIn('IFPLASTEX1', text)
        self.assertNotIn('IFNOTPLASTEX1', text)
        self.assertIn('IFPLASTEX2', text)
        self.assertNotIn('IFNOTPLASTEX2', text)

        r = pypdf.PdfReader(self.build_dir / 'test.pdf')
        pdf_text = r.pages[0].extract_text()
        self.assertNotIn('IFPLASTEX1', pdf_text)
        self.assertIn('IFNOTPLASTEX1', pdf_text)
        self.assertNotIn('IFPLASTEX2', pdf_text)
        self.assertIn('IFNOTPLASTEX2', pdf_text)
