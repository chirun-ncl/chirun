from plasTeX import Command
from plasTeX.Tokenizer import Token
from plasTeX.Logging import getLogger

log = getLogger()


class label(Command):
    args = "label:id"

    def invoke(self, tex):
        # Allow _ character in labels
        catcode = self.ownerDocument.context.whichCode('_')
        self.ownerDocument.context.catcode('_', Token.CC_LETTER)
        self.parse(tex)
        self.ownerDocument.context.catcode('_', catcode)
