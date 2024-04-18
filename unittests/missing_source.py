from . import ExpectCrashTest

class MissingSourceTest(ExpectCrashTest):
    source_path = 'missing_source'

    def test_missing_source(self):
        """ Check that an item in the config with no source defined produces an error.

            Tests https://github.com/chirun-ncl/chirun/issues/217
        """

        self.assertNotEqual(self.compilation.returncode, 0)
        self.assertIn(r'''The item "Untitled chapter" has no source defined.''', self.compilation.stderr)

class IncorrectSourceTest(ExpectCrashTest):
    source_path = 'missing_source'
    compile_args = ['--config','incorrect_source.yml']

    def test_missing_source(self):
        """ Check that an item in the config whose source file does not exist produces an error.

            Tests https://github.com/chirun-ncl/chirun/issues/217
        """

        self.assertNotEqual(self.compilation.returncode, 0)
        self.assertIn(r'''The specified source of the item "Untitled chapter", at missing.tex, does not exist.''', self.compilation.stderr)
