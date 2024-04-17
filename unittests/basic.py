from . import ChirunCompilationTest

class BasicTest(ChirunCompilationTest):
    source_path = 'basic'

    """
        Compile a single LaTeX document with almost nothing in it, and check that the general layout is correct.
    """

    def test_compilation_succeeded(self):
        self.assertEqual(self.compilation.returncode, 0)

    def test_chapter_dir_exists(self):
        latex_document_dir = self.build_dir / 'basic_latex_document'
        self.assertTrue(latex_document_dir.exists(), msg=f'{latex_document_dir} exists')

    def test_links(self):
        intro = self.get_soup('index.html')

        item_links = intro.select('.chirun-structure .item .contents > li > a')
        self.assertEqual(len(item_links), 2, msg="There are two items")
        item_link = item_links[0]
        self.assertEqual(item_link['href'], 'basic_latex_document/index.html', msg="The links to items are relative")

    def test_metadata(self):
        """
            Test that package metadata is included in the manifest and the introduction page.
            
            Tests https://github.com/chirun-ncl/chirun/issues/7
        """
        manifest = self.get_manifest()

        self.assertEqual(manifest['author'], "U. Nittest")
        self.assertEqual(manifest['institution'], "Testing University")
        self.assertEqual(str(manifest['year']), "3435")
        self.assertEqual(manifest['code'], "UT0001")
        self.assertEqual(manifest['license']['name'], "CC-BY 4.0")

        intro = self.get_soup('index.html')
        self.assertEqual(intro.find(class_="author").text, 'U. Nittest')
        self.assertEqual(intro.find(class_="year").text, '3435')
        license_text = intro.find(class_="license-info").text
        self.assertIn('©', license_text)
        self.assertIn('3434', license_text)
        self.assertIn('CC-BY 4.0', license_text)
        self.assertIn('People', license_text)
        self.assertEqual(intro.select_one('.license-info a')['href'], 'https://creativecommons.org/licenses/by/4.0/deed.en')

    def test_structure(self):
        manifest = self.get_manifest()

        self.assertEqual(len(manifest['structure']), 3, msg="There are two items in the structure.")
        self.assertEqual([x['type'] for x in manifest['structure']], ['introduction', 'chapter', 'chapter'], msg="There is an introduction and two chapters.")

    def test_empty_links(self):
        """ Check that all links on the introduction page contain readable text.
            
            Tests https://github.com/chirun-ncl/chirun/issues/12
        """
        intro = self.get_soup('index.html')

        self.assertFalse(any(a.text == '' for a in intro.find_all('a')), msg='All links contain text')

    def test_file_build_time(self):
        """ Check that URLs of static files have a ``build_time`` query parameter added, to prevent caching.

            Tests https://github.com/chirun-ncl/chirun/issues/199
        """

        intro = self.get_soup('index.html')

        for link in intro.select('link'):
            if link['href'].startswith('http'):
                continue
            self.assertIn('build_time=', link['href'])

        for script in intro.select('script[src]'):
            if script['src'].startswith('http'):
                continue
            self.assertIn('build_time=', script['src'])

class BasicStandaloneTest(ChirunCompilationTest):
    """
        Compile a single LaTeX document in standalone mode.
    """

    source_path = 'basic'
    compile_args = ['-f','test.tex']

    def test_standalone_compilation(self):
        self.assertEqual(self.compilation.returncode, 0)

    def test_index_exists(self):
        self.assertTrue((self.build_dir / 'index.html').exists())

    def test_structure(self):
        manifest = self.get_manifest()

        self.assertEqual(len(manifest['structure']), 1, msg="There is only one item in the structure.")


