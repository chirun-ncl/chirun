from . import ChirunCompilationTest

class EnvironmentTest(ChirunCompilationTest):
    source_path = 'latex_environments'
    compile_args = ['-f', 'test.tex']

    def test_newenvironment(self):
        """ Test that `\newenvironment works without errors.

            Tests https://github.com/chirun-ncl/chirun/issues/53
        """
        soup = self.get_soup('index.html')

        self.assertIn('Start! Middle! End!', soup.select_one('.item-content').text)
