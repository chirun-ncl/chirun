from . import ChirunCompilationTest

class NotebookTest(ChirunCompilationTest):
    source_path = 'notebook'

    def test_comments(self):
        """ Test that HTML comments and unused link labels are not present in the HTML output.

            Tests https://github.com/chirun-ncl/chirun/issues/118
        """
        with open(self.build_dir / 'comments' / 'index.html') as f:
            text = f.read()
        self.assertNotIn('COMMENT1', text, msg="HTML comment on its own line is stripped")
        self.assertNotIn('COMMENT2', text, msg="Inline HTML comment is stripped")
        self.assertNotIn('COMMENT3', text, msg="Unused link label is not used")
