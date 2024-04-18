from . import ChirunCompilationTest
import json

class RefsTest(ChirunCompilationTest):
    source_path = 'refs'
    compile_args = ['-f', 'refs.tex']

    expect_labels = {'s1': {'ref': '1', 'url': '#s1'}, 'e1a': {'ref': '1a', 'url': '#e1a'}, 'e1b': {'ref': '1b', 'url': '#e1b'}, 'e2': {'ref': '2', 'url': '#e2'}, 'ez': {'ref': 'z', 'url': '#ez'}, 's2': {'ref': '3', 'url': '#s2'}, 'e2a': {'ref': '3a', 'url': '#e2a'}, 'e2y': {'ref': 'y', 'url': '#e2y'}, 'e2b': {'ref': '3b', 'url': '#e2b'}}

    def setUp(self):
        self.soup = self.get_soup('index.html')

    def test_labels_json(self):
        """ Check that the JSON encoding of labels in the page is correct.

            Tests https://github.com/chirun-ncl/chirun/issues/219
        """

        labels_tag = self.soup.find(id='plastex-labels')
        labels = json.loads(labels_tag.text)

        self.assertEqual(self.expect_labels, labels)

    def test_label_ids(self):
        """ Check that for each label, there is an element with that ID.
        """

        for label in self.expect_labels.keys():
            el = self.soup.find(id=label)
            self.assertIsNotNone(el)

    def test_textmode_refs(self):
        """ Check that the ``\ref`` command in text mode links to the right thing.
        """

        textmode_p = self.soup.select('.item-content p')[-2]

        expect_links = [
            ('#s1', '1'),
            ('#e1a', '1a'),
            ('#e1b', '1b'),
            ('#e2', '2'),
            ('#ez', 'z'),
            ('#s2', '3'),
            ('#e2a', '3a'),
            ('#e2y', 'y'),
            ('#e2b', '3b'),
        ]

        links = textmode_p.select('a')
        for i, (href, text) in enumerate(expect_links):
            a = links[i]
            self.assertEqual(a['href'], href)
            self.assertEqual(a.text.strip(), text)

    def test_mathmode_refs(self):
        """ Check that the ``\ref`` command in math mode contains the right reference.
        """

        mathmode_p = self.soup.select('.item-content p')[-1]

        self.assertEqual(mathmode_p.text.strip(), r'Refs in maths mode: \( \ref{s1} \ref{e1a} \ref{e1b} \ref{e2} \ref{ez} \ref{s2} \ref{e2a} \ref{e2y} \ref{e2b} \)')
