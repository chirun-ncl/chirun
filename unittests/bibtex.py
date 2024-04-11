from . import ChirunCompilationTest

class BibtexTest(ChirunCompilationTest):
    source_path = 'bibtex'
    compile_args = ['-f', 'test.tex']

    def test_citation(self):
        """ Test that citations are processed in one go.
            
            Tests https://github.com/chirun-ncl/chirun/issues/37
        """
        soup = self.get_soup('index.html')

        cite = soup.select_one('.cite')
        self.assertIn("Person, 1729", cite.text)
        self.assertEqual(cite.select_one('a')['href'], '#citation')

        bibliography = soup.select_one('section.bibliography')
        self.assertIsNotNone(bibliography, msg="The bibliography section is included.")
        citation = bibliography.find(id='citation')
        self.assertIsNotNone(citation, msg="The citation item is included.")
        self.assertIn("Person, A. (1729). Article title. Journal of Testing, 1(2):3–4.", citation.text)
