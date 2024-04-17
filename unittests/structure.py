from . import ChirunCompilationTest

class StructureTest(ChirunCompilationTest):
    """ Tests to do with the structure of a course.
    """

    source_path = 'structure'

    compile_args = ['--hash-salt', 'a']

    def test_duplicated_item(self):
        """ Items with the same title will have different slugs.

            Tests https://github.com/chirun-ncl/chirun/issues/51
        """

        manifest = self.get_manifest()

        self.assertEqual(manifest['structure'][1]['title'], 'Duplicated')
        self.assertEqual(manifest['structure'][1]['url'], 'duplicated/index.html')
        self.assertEqual(manifest['structure'][2]['title'], 'Duplicated')
        self.assertEqual(manifest['structure'][2]['url'], 'duplicat_1/index.html')
        self.assertEqual(manifest['structure'][3]['title'], 'Duplicated')
        self.assertEqual(manifest['structure'][3]['url'], 'duplicat_2/index.html')

    def test_truncated_slug(self):
        """ Items with long titles will have their slugs truncated to 20 characters.

            Tests https://github.com/chirun-ncl/chirun/issues/51 and https://github.com/chirun-ncl/chirun/issues/201
        """

        manifest = self.get_manifest()

        self.assertEqual(manifest['structure'][4]['slug'], 'a_very_long_title_wh')
        self.assertLessEqual(len(manifest['structure'][4]['slug']), 20)
        self.assertEqual(manifest['structure'][5]['slug'], 'a_very_long_title_1')
        self.assertLessEqual(len(manifest['structure'][5]['slug']), 20)

    def test_hidden_item(self):
        """ Check that items with ``is_hidden: true`` get a hash added to their path, and aren't included in the index page.

            Tests https://github.com/chirun-ncl/chirun/issues/197
        """
        hidden_part_path = 'hidden_part-80bfe7b2'
        hidden_chapter_path = 'hidden_chapter-b04b7865'

        self.assertTrue((self.build_dir / hidden_part_path).exists())
        self.assertTrue((self.build_dir / hidden_chapter_path).exists())

        with open(self.build_dir / 'index.html') as f:
            index = f.read()

        self.assertNotIn('Hidden part', index)
        self.assertNotIn('Hidden chapter', index)
        self.assertNotIn(hidden_part_path, index)
        self.assertNotIn(hidden_chapter_path, index)
        self.assertNotIn('Not explicitly hidden', index)
        self.assertNotIn('not_explicitly_hidd', index)

    def test_unicode_slug(self):
        """ Tests that slashes are removed from slugs, but unicode letters are kept.
        """

        manifest = self.get_manifest()

        self.assertEqual(manifest['structure'][8]['slug'], 'a_𝑎𝐚𝒜')
