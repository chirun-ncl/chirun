from . import ChirunCompilationTest

class SlashTest(ChirunCompilationTest):
    source_path = 'slash'
    compile_args = ['-f', 'test.tex', '--no-pdf']

    def test_slash(self):
        r""" 
            Check that the ``\slash`` command is interpreted and produces a forward slash character.

            Tests https://github.com/chirun-ncl/chirun/issues/211
        """
        soup = self.get_soup('index.html')

        paras = soup.select('.item-content p')

        self.assertEqual(paras[0].text.strip(), 'A /in text / mode.')
        self.assertEqual(paras[1].text.strip(), r'\(m \slash n\)')
