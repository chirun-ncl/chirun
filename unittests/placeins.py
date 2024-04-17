from . import ChirunCompilationTest

class PlaceinsTest(ChirunCompilationTest):
    source_path = 'placeins'
    compile_args = ['-f','test.tex', '--no-pdf']

    def test_floatbarrier(self):
        """ The ``\FloatBarrier`` command shouldn't stop HTML output from working'

            Tests https://github.com/chirun-ncl/chirun/issues/164
        """
        pass
