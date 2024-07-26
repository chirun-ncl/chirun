from . import ChirunCompilationTest

class MDFigureTest(ChirunCompilationTest):
    source_path = 'mdfigure'
    compile_args = ['-f','test.md', '--no-pdf']

    """
        Compile a markdown document with some images, and check that they're placed in ``<figure>`` elements appropriately.
    """

    def test_figures(self):
        soup = self.get_soup('index.html')

        images = soup.select('img')

        parent_tags = {
            'a': 'figure',
            'b': 'p',
            'c': 'figure',
            'd': 'figure',
        }

        for image in images:
            expected_parent_tag = parent_tags[image['src'][0]]
            assert image.parent.name == expected_parent_tag, f"Image {image['src']} should be under a {expected_parent_tag} tag."

        figure_children = [
            ['a1', 'a2', 'a3', 'a4'],
            ['c1', 'c2'],
            ['d1'],
            ['d2'],
            ['d3'],
            ['d4'],
        ]

        figures = soup.select('figure')

        for i, expected_children in enumerate(figure_children):
            figure = figures[i]
            children_alts = [image['alt'] for image in figure.select('img')]
            assert children_alts == expected_children
