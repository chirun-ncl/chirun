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

    def test_structure(self):
        manifest = self.get_manifest()

        self.assertEqual(len(manifest['structure']), 3, msg="There are two items in the structure.")
        self.assertEqual([x['type'] for x in manifest['structure']], ['introduction', 'chapter', 'chapter'], msg="There is an introduction and two chapters.")

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


