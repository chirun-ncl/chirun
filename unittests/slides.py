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
