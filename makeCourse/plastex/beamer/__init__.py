from plasTeX.Packages.beamer import *
import plasTeX.Packages.beamer

class column(plasTeX.Packages.beamer.column):
    args = '[ placement ] width:dimen'

class columnenv(Environment):
    args = column.args
