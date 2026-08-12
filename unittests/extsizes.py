from . import ChirunCompilationTest

class ExtSizesTest(ChirunCompilationTest):
    source_path = 'extsizes'

    compile_args = ['--config', 'config.yml',]

    def test_ifplastex(self):
        r""" 
            Test that the extsizes documentclasses safely compile (with no impact on the html text size)

            Tests https://github.com/chirun-ncl/chirun/issues/312
        """
        #article
        soup = self.get_soup('extarticle/index.html')
        self.assertIn('bigger', soup.select_one('.item-content').text)

        #book
        soup = self.get_soup('extbook/index.html')
        self.assertIn('bigger', soup.select_one('.item-content').text)
        
        #letter
        soup = self.get_soup('extletter/index.html')
        self.assertIn('bigger', soup.select_one('.item-content').text)
        
        #proc
        soup = self.get_soup('extproc/index.html')
        self.assertIn('bigger', soup.select_one('.item-content').text)
        
        #report
        soup = self.get_soup('extreport/index.html')
        self.assertIn('bigger', soup.select_one('.item-content').text)
