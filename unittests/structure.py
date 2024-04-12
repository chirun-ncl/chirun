from . import ChirunCompilationTest

class StructureTest(ChirunCompilationTest):
    """ Tests to do with the structure of a course.
    """

    source_path = 'structure'

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

            Tests https://github.com/chirun-ncl/chirun/issues/51
        """

        manifest = self.get_manifest()

        self.assertEqual(manifest['structure'][4]['slug'], 'a_very_long_title_wh')
        self.assertLessEqual(len(manifest['structure'][4]['slug']), 20)
        self.assertEqual(manifest['structure'][5]['slug'], 'a_very_long_title_1')
        self.assertLessEqual(len(manifest['structure'][5]['slug']), 20)
