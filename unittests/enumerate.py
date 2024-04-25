from . import ChirunCompilationTest

class EnumerateTest(ChirunCompilationTest):
    source_path = 'enumerate'

    compile_args = ['-f', 'test.tex', '--no-pdf']

    def test_nested_enumerate(self):
        """ Test the labelling of nested enumerate environments.

            Tests https://github.com/chirun-ncl/chirun/issues/235
        """

        soup = self.get_soup('index.html')

        sections = soup.select('.item-content > section')

        default_ols = sections[0].select('.enumerate')
        for ol in default_ols:
            self.assertNotIn('custom-terms', ol['class'])
        for li in sections[0].select('li'):
            self.assertIsNone(li.select_one('.list-item-marker'))

        some_custom_ols = sections[1].select('ol')
        for ol in some_custom_ols:
            self.assertIn('custom-terms', ol['class'])

        li_markers = [marker.text for marker in sections[1].select('.list-item-marker')]
        self.assertEqual(li_markers, ['1.', '2.', '(a)', 'i.', 'A.', '::', '–', '(b)', '?', '3.', '!!!'])

        default_marker = some_custom_ols[0].li.select_one('.list-item-marker')
        self.assertIn('default-marker', default_marker['class'])

        custom_marker = some_custom_ols[0].find_all('li')[-1].select_one('.list-item-marker')
        self.assertNotIn('default-marker', custom_marker['class'])
        self.assertEqual(custom_marker.text, '!!!')

        custom_ols = sections[2].select('ol')
        self.assertIn('custom-terms', custom_ols[0]['class'])
        li_markers = [marker.text for marker in sections[2].select('.list-item-marker')]
        self.assertEqual(li_markers, ['<1>', '<2>', "'I'", '...a', "'II'", '<3>'])
