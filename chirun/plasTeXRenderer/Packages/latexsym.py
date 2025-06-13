
from plasTeX import Macro
from plasTeX.Tokenizer import Other
class LiteralMathSymbol(Macro):
    def invoke(self, tex):
        return [Other(self.str)]

class mho(LiteralMathSymbol): str = '℧'
class Join(LiteralMathSymbol): str = '⨝'
class Box(LiteralMathSymbol): str = '☐'
class Diamond(LiteralMathSymbol): str = '◇'
class leadsto(LiteralMathSymbol): str = '⤳'
class sqsubset(LiteralMathSymbol): str = '⊏'
class sqsupset(LiteralMathSymbol): str = '⊐'
class lhd(LiteralMathSymbol): str = '⊲'
class unlhd(LiteralMathSymbol): str = '⊴'
class rhd(LiteralMathSymbol): str = '⊳'
class unrhd(LiteralMathSymbol): str = '⊵'