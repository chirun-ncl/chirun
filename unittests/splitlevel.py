from . import ChirunCompilationTest
import pypdf

class SplitlevelTest(ChirunCompilationTest):
    source_path = 'splitlevel'
    show_stderr = False

    def test_pdf_splitlevel(self):
        pdfs = {
            'default_splitlevel': {
                'a.pdf': 8,
                'aa.pdf': 2,
                'ab.pdf': 2,
                'b.pdf': 3,
            },
            'no_splitting': {
                'test.pdf': 11
            },
            'split_at_part': {
                'a.pdf': 8,
                'b.pdf': 3,
            },
            'split_at_chapter': {
                'a.pdf': 8,
                'aa.pdf': 2,
                'ab.pdf': 2,
                'b.pdf': 3,
            },
            'split_at_section': {
                'a.pdf': 8,
                'aa.pdf': 2,
                'aaa.pdf': 2,
                'aab.pdf': 2,
                'ab.pdf': 2,
                'aba.pdf': 2,
                'abb.pdf': 2,
                'b.pdf': 3,
            },
            'split_at_subsection': {
                'a.pdf': 8,
                'aa.pdf': 2,
                'aaa.pdf': 2,
                'aaaa.pdf': 2,
                'aaab.pdf': 2,
                'aab.pdf': 2,
                'ab.pdf': 2,
                'aba.pdf': 2,
                'abb.pdf': 2,
                'b.pdf': 3,
            },
            'no_hyperref': {
                'no_hyperref.pdf': 11
            },
        }

        for item, file_info in pdfs.items():
            files = file_info.keys()
            pdf_dir = self.build_dir / item / 'pdf'
            pdf_files = [f.name for f in pdf_dir.iterdir() if f.suffix == '.pdf']
            self.assertEqual(set(pdf_files), set(files), msg=f"Files in {item}")
            for filename, num_pages in file_info.items():
                with open(pdf_dir / filename, 'rb') as f:
                    r = pypdf.PdfReader(f)
                    self.assertEqual(r.get_num_pages(), num_pages, msg=f'{filename} has {num_pages} pages')

    def test_pdf_links(self):
        """ Check that links to PDFs for each item are correct.

            Tests https://github.com/chirun-ncl/chirun/issues/204
        """

        manifest = self.get_manifest()

        def get_pdf(item):
            for f in item['formats']:
                if f['filetype'] == 'pdf':
                    return f['url']


        a = manifest['structure'][1]['content'][0]
        b = manifest['structure'][1]['content'][1]
        self.assertEqual(get_pdf(a), 'default_splitlevel/pdf/a.pdf')
        self.assertEqual(get_pdf(b), 'default_splitlevel/pdf/b.pdf')
        aa = a['content'][0]
        self.assertEqual(get_pdf(aa), 'default_splitlevel/pdf/aa.pdf')
