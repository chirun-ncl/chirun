from . import ChirunCompilationTest

class RunnableCodeTest(ChirunCompilationTest):
    source_path = 'runnable_code'

    def test_latex_runnable_code(self):
        """ Checks that the ``runnableCode`` environment is defined in LaTeX and produces a <runnable-code> element in HTML.

            Tests https://github.com/chirun-ncl/chirun/issues/155
            and   https://github.com/chirun-ncl/chirun/issues/160
        """
        soup = self.get_soup('latex_runnable_code/index.html')

        runnables = soup.select('runnable-code')
        self.assertEqual(len(runnables), 1)
        self.assertEqual(runnables[0].text, '''
if False:
    print(3**3**3**3**3)
'''.strip())

    def test_latex_runnable_code(self):
        """ Checks that the ``runnable`` annotation for code blocks is defined in LaTeX and produces a <runnable-code> element in HTML.
        """
        soup = self.get_soup('markdown_runnable_co/index.html')

        runnables = soup.select('runnable-code')
        self.assertEqual(len(runnables), 1)
