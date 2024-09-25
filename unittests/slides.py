from . import ChirunCompilationTest

class SlidesTest(ChirunCompilationTest):
    source_path = 'slides'

    def test_beamer_slides_author(self):
        r"""
            Test that the author field for the slides item is used, instead of the package's author.
            
            Tests https://github.com/chirun-ncl/chirun/issues/14
        """
        soup = self.get_soup('beamer_slides/beamer_slides.slides.html')

        self.assertEqual(soup.select_one('#slides-author').text, 'A.N. Other')
        self.assertEqual(soup.select_one('#title-slide .author').text, 'A.N. Other')

    def test_beamer_slide_title(self):
        r""" 
            Test that a frame with a given title has that title displayed in the HTML slides version.
        
            Tests https://github.com/chirun-ncl/chirun/issues/28
        """

        soup = self.get_soup('beamer_slides/beamer_slides.slides.html')

        self.assertEqual(soup.select('.beamer-frame')[2].select_one('.beamer-frame-title').text, 'First frame title')
        self.assertEqual(soup.select('.beamer-frame')[3].select_one('.beamer-frame-title').text, 'Title as param')

    def test_beamer_slides_tableofcontents(self):
        r""" 
            Test that a table of contents is produced, with a link to each section.

            Tests https://github.com/chirun-ncl/chirun/issues/48
        """

        soup = self.get_soup('beamer_slides/beamer_slides.slides.html')

        contents_slide = soup.select('.beamer-frame')[0]
        self.assertEqual(contents_slide.select_one('.beamer-frame-title').text, 'Contents')
        self.assertEqual(len(contents_slide.select('a')), 1)
        self.assertEqual(contents_slide.select_one('a').text.strip(), 'Section')

    def test_beamer_loads_hyperref(self):
        r"""
            Test that the beamer documentclass loads the hyperref package.

            Tests https://github.com/chirun-ncl/chirun/issues/103
        """

        soup = self.get_soup('beamer_slides/beamer_slides.slides.html')

        a = soup.find(id='link').parent.parent.select_one('a')
        self.assertIsNotNone(a)
        self.assertEqual(a['href'], 'https://example.com')
        self.assertEqual(a.text, 'Example')

    def test_appendixnumberbeamer(self):
        r"""
            Test that the appendixnumberbeamer package loads.

            Tests https://github.com/chirun-ncl/chirun/issues/40
        """

        self.assertTrue((self.build_dir / 'appendix_number' / 'index.html').exists())

    def test_pause(self):
        r"""
            The \pause command is removed from any math expressions.

            Tests https://github.com/chirun-ncl/chirun/issues/58
        """

        soup = self.get_soup('beamer_slides/beamer_slides.slides.html')

        pause_frame = soup.find(id='pause_in_maths').parent.parent
        self.assertNotIn(r'\pause', pause_frame.select_one('p').text)
