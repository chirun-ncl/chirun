#!/usr/bin/env python

import os
import subprocess
import os
import binascii
import shlex
from plasTeX.Imagers.pdftoppm import pdftoppm
from pathlib import Path

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
