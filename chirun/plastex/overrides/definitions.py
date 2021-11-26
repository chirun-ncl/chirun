from plasTeX import NewCommand
from plasTeX.Tokenizer import Tokenizer
from plasTeX.Logging import getLogger
from plasTeX.Context import Context

log = getLogger()


def newcommand(self, name, nargs=0, definition=None, opt=None):
    if nargs is None:
        nargs = 0
    assert isinstance(nargs, int), 'nargs must be an integer'

    if isinstance(definition, str):
        definition = [x for x in Tokenizer(definition, self)]

    if isinstance(opt, str):
        opt = [x for x in Tokenizer(opt, self)]

    newclass = type(name, (NewCommand,), {'nargs': nargs, 'opt': opt, 'definition': definition})

    self.addGlobal(name, newclass)


Context.newcommand = newcommand


def newenvironment(self, name, nargs=0, def_before=None, def_after=None, opt=None):
    if nargs is None:
        nargs = 0
    assert isinstance(nargs, int), 'nargs must be an integer'

    if def_before:
        def_before = list(Tokenizer(def_before, self))
    if def_after:
        def_after = list(Tokenizer(def_after, self))

    if isinstance(opt, str):
        opt = [x for x in Tokenizer(opt, self)]

    # Begin portion
    newclass = type(name, (NewCommand,), {'nargs': nargs, 'opt': opt, 'definition': def_before})
    self.addGlobal(name, newclass)

    # End portion
    newclass = type('end' + name, (NewCommand,), {'nargs': 0, 'opt': None, 'definition': def_after})
    self.addGlobal('end' + name, newclass)


Context.newenvironment = newenvironment
