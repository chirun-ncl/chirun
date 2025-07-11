from . import ChirunCompilationTest

class EmbedTest(ChirunCompilationTest):
    """
        Tests the tabular environment.
    """
    source_path = 'embed'
    compile_args = ['-f', 'test.tex']

    def test_compilation_succeeded(self):
        self.assertEqual(self.compilation.returncode, 0)

    def test_numbas(self):
        soup = self.get_soup('index.html')

        numbas = soup.find('embed-numbas')

        self.assertEqual(numbas['url'], 'https://numbas.mathcentre.ac.uk/exam/35899/easy-exam/preview')

    def test_vimeo(self):
        soup = self.get_soup('index.html')

        vimeo = soup.select('iframe.vimeo')[0]

        self.assertEqual(vimeo['src'], 'https://player.vimeo.com/video/8169375')

    def test_youtube(self):
        soup = self.get_soup('index.html')

        youtube = soup.select('iframe.youtube')[0]

        self.assertEqual(youtube['src'], 'https://www.youtube.com/embed/88Mzr5JGpsY?ecver=1')

    def test_iframe(self):
        soup = self.get_soup('index.html')

        iframes = soup.select('iframe')

        self.assertEqual(iframes[3]['src'], 'https://chirun.org.uk')

        self.assertEqual(iframes[4]['width'], '500')
        self.assertEqual(iframes[4]['height'], '400')

    def test_audio(self):
        soup = self.get_soup('index.html')

        audio = soup.find('audio')

        self.assertIn('controls', audio.attrs)

        source = audio.find('source')

        self.assertEqual(source['src'], 'static/Court_House_Blues.mp3')

    def test_video(self):
        soup = self.get_soup('index.html')

        videos = soup.select('video')

        self.assertEqual(videos[0].find('source')['src'], 'static/movie.mp4')
        self.assertEqual(videos[1]['width'], '500')
        self.assertEqual(videos[1]['height'], '400')

