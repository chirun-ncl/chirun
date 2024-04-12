from . import ChirunCompilationTest

class VerbatimTest(ChirunCompilationTest):
    source_path = 'verbatim'
    compile_args = ['-f', 'test.tex', '--no-pdf']

    def test_comment_environment(self):
        """ Check that you can define a new environment which wraps a \comment command.

            Tests https://github.com/chirun-ncl/chirun/issues/87
        """

        soup = self.get_soup('index.html')

        self.assertNotIn('Answer', soup.select_one('.item-content').text)
