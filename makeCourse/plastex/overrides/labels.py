from plasTeX import Command
from plasTeX.Tokenizer import Token, Tokenizer, EscapeSequence, Other
from plasTeX.Logging import getLogger
from plasTeX.Context import Context

log = getLogger()

class label(Command):
    args = "label:id"
    def invoke(self, tex):
        # Allow _ character in labels
        catcode = self.ownerDocument.context.whichCode('_')
        self.ownerDocument.context.catcode('_', Token.CC_LETTER)
        a = self.parse(tex)
        self.ownerDocument.context.catcode('_', catcode)
