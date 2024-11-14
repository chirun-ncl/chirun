import subprocess
from plasTeX.Imagers import pdf2svg, Image
from pathlib import Path
import tempfile


class PDFSVG(pdf2svg.PDFSVG):
    """ Imager that uses pdf2svg. """

    # Overridden to run pdf2svg directly on PDF files, instead of sending them through the LaTeX compiler.
    def getImage(self, node):
        name = getattr(node, 'imageoverride', None)

        if name in self.staticimages:
            return self.staticimages[name]

        if name is not None:
            suffix = Path(name).suffix.lower()
            if suffix == '.pdf':
                return self.single_pdf_to_svg(name)
            elif suffix == '.eps':
                return self.single_eps_to_pdf(name)

        return super().getImage(node)

    def single_eps_to_pdf(self, name):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            pdf_path = tmpdir / 'image.pdf'
            subprocess.run(['epstopdf', name, pdf_path],errors="backslashreplace")
            return self.single_pdf_to_svg(pdf_path)

    def single_pdf_to_svg(self, name):
        """
            Convert a single PDF file to an SVG file.

            Returns:
                plasTeX.Imagers.Image
        """
        path = self.newFilename()
        Path(path).parent.mkdir(exist_ok=True, parents=True)
        cmd = ['pdf2svg', name, path]
        subprocess.run(cmd)
        img = Image(path, self.ownerDocument.config['images'])
        self.staticimages[name] = img
        return img


Imager = PDFSVG
