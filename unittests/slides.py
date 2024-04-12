from . import ChirunCompilationTest

class SlidesTest(ChirunCompilationTest):
    source_path = 'slides'

    def test_beamer_slides_author(self):
        """ Test that the author field for the slides item is used, instead of the package's author.
            
            Tests https://github.com/chirun-ncl/chirun/issues/14
        """
        soup = self.get_soup('beamer_slides/beamer_slides.slides.html')

        self.assertEqual(soup.select_one('#slides-author').text, 'A.N. Other')
        self.assertEqual(soup.select_one('#title-slide .author').text, 'A.N. Other')

    def test_beamer_slide_title(self):
        """ Test that a frame with a given title has that title displayed in the HTML slides version.
        
            Tests https://github.com/chirun-ncl/chirun/issues/28
        """

        soup = self.get_soup('beamer_slides/beamer_slides.slides.html')

        self.assertEqual(soup.select('.beamer-frame')[0].select_one('.beamer-frame-title').text, 'First frame title')
        self.assertEqual(soup.select('.beamer-frame')[1].select_one('.beamer-frame-title').text, 'Title as param')

    def test_appendixnumberbeamer(self):
        """ Test that the appendixnumberbeamer package loads.

            Tests https://github.com/chirun-ncl/chirun/issues/40
        """
        self.assertTrue((self.build_dir / 'appendix_number' / 'index.html').exists())
