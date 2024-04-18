from . import ChirunCompilationTest
import re

class ProofTest(ChirunCompilationTest):
    source_path = 'proof'

    def test_newenvironment(self):
        """ Checks how a proof environment defined with ``\\newenvironment`` is displayed, without the amsthm package.
        """
        soup = self.get_soup('newenvironment/index.html')

        p = soup.select_one('.item-content p')
        self.assertNotIn('class', p)
        self.assertEqual(p.text.strip(), 'Begin Proof Proof environment. End Proof')

    def test_newenvironment_amsthm(self):
        """ Checks how a proof environment defined with ``\\newenvironment`` is displayed, with the amsthm package loaded.
        """
        soup = self.get_soup('newenvironment_amsth/index.html')

        proofwrapper = soup.select_one('.proof_wrapper')
        self.assertIsNotNone(proofwrapper)
        proofheading = proofwrapper.select_one('.proof_heading')
        self.assertEqual(proofheading.name, 'h6')
        self.assertEqual(re.sub(r'\s+', ' ',proofheading.text.strip(), re.M), 'Proof.')
        proofcontent = proofwrapper.select_one('.proof_content')
        self.assertEqual(proofcontent.text.strip(), 'Proof environment.')

    def test_amsthm(self):
        """ Checks how a proof environment defined with the ``amsthm`` package's ``\newtheorem`` command is displayed.

            Tests https://github.com/chirun-ncl/chirun/issues/218
        """
        soup = self.get_soup('amsthm/index.html')

        thmwrapper = soup.select_one('.thmwrapper')
        self.assertIsNotNone(thmwrapper)
        thmheading = thmwrapper.select_one('.thmheading')
        self.assertEqual(thmheading.name, 'h5')
        self.assertEqual(re.sub(r'\s+', ' ',thmheading.text.strip(), re.M), 'Theorem 1')
        thmcontent = thmwrapper.select_one('.thmcontent')
        self.assertEqual(thmcontent.text.strip(), 'Theorem environment.')

        proofwrapper = soup.select_one('.proof_wrapper')
        self.assertIsNotNone(proofwrapper)
        proofheading = proofwrapper.select_one('.proof_heading')
        self.assertEqual(proofheading.name, 'h6')
        self.assertEqual(re.sub(r'\s+', ' ',proofheading.text.strip(), re.M), 'Proof.')
        proofcontent = proofwrapper.select_one('.proof_content')
        self.assertEqual(proofcontent.text.strip(), 'Proof environment.')
