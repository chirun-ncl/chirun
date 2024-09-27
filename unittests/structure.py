from . import ChirunCompilationTest

from pathlib import Path
import os
import zipfile

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
        """ Check that items with ``is_hidden: true`` get a hash added to their path, and aren't included in the index page or the manifest.

            But hidden sub-items should be linked from the index pages of their parent part.

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

        manifest = self.get_manifest()

        def all_items(items):
            for item in items:
                yield item
                if 'content' in item:
                    yield from all_items(item['content'])

        all_slugs = list(x['slug'] for x in all_items(manifest['structure']))

        self.assertNotIn('hidden_chapter', all_slugs)
        self.assertNotIn('hidden_part', all_slugs)
        self.assertNotIn('not_explicitly_hidde', all_slugs)

        hidden_soup = self.get_soup(self.build_dir / 'hidden_part-80bfe7b2' / 'index.html')

        item_links = hidden_soup.select('.chirun-structure .item .contents > li > a')
        self.assertEqual(len(item_links), 1, msg="There is one item under the hidden part.")
        item_link = item_links[0]
        self.assertEqual(item_link['href'], 'not_explicitly_hidde-c80aca75/index.html', msg="The not explicity hidden item is linked from its parent's index.")

    def test_unicode_slug(self):
        """ Tests that slashes are removed from slugs, but unicode letters are kept.
        """

        manifest = self.get_manifest()

        self.assertEqual(manifest['structure'][8]['slug'], 'a_𝑎𝐚𝒜')

    def test_next_prev_links(self):
        """ Check that the next/previous item links on each page are present and point to the expected things.

            Tests https://github.com/chirun-ncl/chirun/issues/203
        """

        soup = self.get_soup('duplicated/index.html')
        self.assertEqual(soup.select_one('a[rel="prev"]')['href'], '../index.html')
        self.assertEqual(soup.select_one('a[rel="next"]')['href'], '../duplicat_1/index.html')

        soup = self.get_soup('duplicat_1/index.html')
        self.assertEqual(soup.select_one('a[rel="prev"]')['href'], '../duplicated/index.html')
        self.assertEqual(soup.select_one('a[rel="next"]')['href'], '../duplicat_2/index.html')

        soup = self.get_soup('a_part/index.html')
        self.assertEqual(soup.select_one('a[rel="next"]')['href'], 'a_chapter/index.html')

        soup = self.get_soup('a_part/a_chapter/index.html')
        self.assertEqual(soup.select_one('a[rel="prev"]')['href'], '../index.html')
        self.assertEqual(soup.select_one('a[rel="next"]')['href'], '../../a_second_part/index.html')

        soup = self.get_soup('a_second_part/a_second_chapter/index.html')
        self.assertEqual(soup.select_one('a[rel="next"]')['href'], '../../a_𝑎𝐚𝒜/index.html', msg="The links should skip over hidden items, and their children.")

    def test_zipfile(self):
        """ Check that all build files apart from those belonging to hidden items are included in the zip.

            Tests #207
        """
        zf = zipfile.ZipFile(self.build_dir / 'course_structure_tes.zip')

        zip_filenames = [f.filename for f in zf.filelist]

        self.assertFalse(any('hidden' in filename for filename in zip_filenames), msg="No hidden files in the zip file")

        disk_filenames = []
        for dirpath, dirnames, filenames in os.walk(self.build_dir, topdown=True):
            for i in range(len(dirnames)-1, 0, -1):
                if 'hidden' in dirnames[i]:
                    del dirnames[i]

            for filename in filenames:
                p = Path(dirpath, filename).relative_to(self.build_dir)
                if p.suffix == '.zip':
                    continue
                if p.name == 'MANIFEST_hidden.json':
                    continue
                disk_filenames.append(str(p))

        self.assertEqual(set(disk_filenames), set(zip_filenames))

class StandaloneTest(ChirunCompilationTest):
    source_path = 'structure'

    compile_args = ['-f', 'basic.tex']

    def test_standalone_no_navigation(self):
        """ Check that a standalone document doesn't have any links to other items.

            Tests https://github.com/chirun-ncl/chirun/issues/224
        """

        soup = self.get_soup('index.html')

        self.assertIsNone(soup.select_one('.breadcrumbs'), msg="No breadcrumbs")
        self.assertIsNone(soup.select_one('#item-pager'), msg="No pager")
