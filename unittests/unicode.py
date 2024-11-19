from . import ChirunCompilationTest


class UnicodeTest(ChirunCompilationTest):
    source_path = 'unicode'
    compile_args = ['-f', 'test.tex']


    def test_unicode(self):
        """
        Tests that raw unicode characters which are not formatted in UTF-8 do not cause crashes

        Tests https://github.com/chirun-ncl/chirun/issues/271
        """
        soup = self.get_soup('index.html')
        paras = soup.select('.item-content p')
        #A break of issue #271 will result in pdfLaTeX failing to compile and the log output recording a subset of the bytes needed to represent the power 2.
        
        self.assertIn("This is a line containing ².",paras[0].text, msg = 'The document has compiled and the unicode character is in the webpage')
