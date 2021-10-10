from plasTeX.Imagers.pdftoppm import pdftoppm


class PDFPPM(pdftoppm):
    def writePreamble(self, document):
        ret = super().writePreamble(document)
        self.source.write(r'''
\ifcsname setbeamerfont\endcsname
\setbeamertemplate{background canvas}[default]
\setbeamercolor{background canvas}{bg=}
\beamertemplatenavigationsymbolsempty
\fi
''')
        return ret


Imager = PDFPPM
