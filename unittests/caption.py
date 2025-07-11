from . import ChirunCompilationTest

class CaptionTest(ChirunCompilationTest):
    """
        Tests the tabular environment.
    """
    source_path = 'caption'
    compile_args = ['-f', 'test.tex']

    def test_compilation_succeeded(self):
        self.assertEqual(self.compilation.returncode, 0)

    def test_caption(self):
        soup = self.get_soup('index.html')

        expected_captions = [
            'Table 0 A small table.',
            'A figure.',
        ]

        for figure, caption in zip(soup.select('figure.minipage'), expected_captions):
            self.assertEqual(figure.find('figcaption').text.strip().replace('\n',' '), caption)
