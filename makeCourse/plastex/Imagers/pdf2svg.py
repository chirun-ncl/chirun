#!/usr/bin/env python

import os
import subprocess
import os
import binascii
import shlex
from plasTeX.Imagers.pdf2svg import PDFSVG as _PDFSVG
from pathlib import Path

class PDFSVG(_PDFSVG):
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

Imager = PDFSVG
