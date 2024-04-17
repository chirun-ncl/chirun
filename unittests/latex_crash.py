from . import ChirunCompilationTest

""" Tests for several ways of making LaTeX compilation fail.

    Tests https://github.com/chirun-ncl/chirun/issues/135
"""

class ExpectCrashTest(ChirunCompilationTest):
    show_stderr = False
    @classmethod
    def check_compilation_returncode(cls):
        pass

class ExtraBraceTest(ExpectCrashTest):
    """ If there is an extra closing brace, pdflatex should quit immediately.
    """
    source_path = 'latex_crash'
    compile_args = ['-f','extra_brace.tex']

    def test_returncode(self):
        self.assertNotEqual(self.compilation.returncode, 0)

class UndefinedCommandTest(ExpectCrashTest):
    """ If an undefined macro is used, pdflatex normally waits for input. 
        Chirun should make it run in noninteractive mode so it quits immediately.
    """
    source_path = 'latex_crash'

    compile_args = ['-f','undefined_command.tex']

    def test_returncode(self):
        self.assertNotEqual(self.compilation.returncode, 0)

class NoEndDocumentTtest(ExpectCrashTest):
    """ If the document environment is not ended, pdflatex normally waits for input. 
        Chirun should make it run in noninteractive mode so it quits immediately.

        Tests https://github.com/chirun-ncl/chirun/issues/168
    """
    source_path = 'latex_crash'

    compile_args = ['-f', 'no_end_document.tex']

    def test_returncode(self):
        self.assertNotEqual(self.compilation.returncode, 0)
