from . import ChirunCompilationTest

class ThemeCustomisationTest(ChirunCompilationTest):
    source_path = 'theme_customisation'

    def test_custom_css(self):
        """ Check that custom.css is imported.
        """

        soup = self.get_soup('index.html')

        self.assertIsNotNone(soup.select('link[rel="stylesheet"][href^="static/custom.css"]'), msg="custom.css is imported")

    def test_custom_js(self):
        """ Check that custom.css is imported.

            Tests https://github.com/chirun-ncl/chirun/issues/63
        """

        soup = self.get_soup('index.html')

        self.assertIsNotNone(soup.select('script[src^="static/custom.js"]'), msg="custom.js is imported")
