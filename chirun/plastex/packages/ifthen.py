"""

A Python implementation of the ifthen package.

"""

from plasTeX import Command, TeXFragment, number
from plasTeX.Tokenizer import Token, Space
from typing import Union, List


class BeginMath(Command):
    macroName = '('
    catcode = None
    disableMath: bool = False

    def invoke(self, tex):
        if self.disableMath:
            return Command.invoke(self, tex)
        o = self.ownerDocument.createElement('math')
        o.macroMode = Command.MODE_BEGIN
        self.ownerDocument.context.push(o)
        return [o]


class EndMath(Command):
    macroName = ')'
    catcode = None
    disableMath: bool = False

    def invoke(self, tex):
        if self.disableMath:
            return Command.invoke(self, tex)
        o = self.ownerDocument.createElement('math')
        o.macroMode = Command.MODE_END
        self.ownerDocument.context.pop(o)
        return [o]


class _boolToken(Token):
    """A placeholder token used to indicate true or false"""
    state: bool = False


class _true(_boolToken):
    state: bool = True


class _false(_boolToken):
    state: bool = False


class IfElseOp(Command):
    catcode = None


class _and(IfElseOp):
    macroName = 'and'


class _not(IfElseOp):
    macroName = 'not'


class _or(IfElseOp):
    macroName = 'or'


class NOT(IfElseOp):
    pass


class AND(IfElseOp):
    pass


class OR(IfElseOp):
    pass


class ifthenelse(Command):
    r"""The \ifthenelse macro.

    This works by first disabling entering math with \( and \) commands.
    Instead they will be used to group expressions in the if test. The
    macros are set back to normal once parsing is complete.

    The argument corresponding to the test statement is expanded, so that the
    result of macros and definitions can be used as part of the expression.

    The expanded tokens are reorganised from an infix expression into a
    postfix expression, then evaluated. The conversion makes for a much
    simpler stack based evaluation.

    Depending on the resulting value of the test expression, the ifthenelse
    macro is expanded into either the "then" argument, or the "else" argument.
    """
    args = 'test:XTok then:nox else:nox'

    def invoke(self, tex) -> List[Token]:
        # Temporarily disable entering math mode with \( and \)
        BeginMath.disableMath = EndMath.disableMath = True
        a = self.parse(tex)
        BeginMath.disableMath = EndMath.disableMath = False
        if isinstance(a['test'], TeXFragment):
            test_result = self.evaluate(tex, a['test'])
        else:
            test_result = self.evaluate(tex, [a['test']])
        return a['then'] if test_result.state else a['else']

    def prec(self, tok: Union[Token, number]) -> int:
        """Return the operator precedence for the given token"""
        if tok == '>' or tok == '<' or tok == '=':
            return 2
        if isinstance(tok, IfElseOp):
            return 1
        return 0

    def evaluate(self, tex, test: Union[List[Token], TeXFragment]) -> _boolToken:
        """Reorganise a test expression into postfix and evaluate it."""
        stack: List[Union[Token, number]] = []
        postfix: List[Union[Token, number]] = []
        test_iter = iter(test)
        for tok in test_iter:
            # Handle literal integers with tex.readNumber
            number_tokens: List[Token] = []
            while tok.catcode == Token.CC_OTHER and (tok not in ['<', '>', '=']):
                number_tokens.append(tok)
                tok = next(test_iter, Space())
            if len(number_tokens) > 0:
                value: int = tex.readInternalType(number_tokens, tex.readNumber)
                postfix.append(number(value))

            # Handle parentheses and booleans
            if tok.catcode == Token.CC_SPACE or tok is None:
                pass
            elif isinstance(tok, _boolToken):
                postfix.append(tok)
            elif tok.nodeName == '(':
                stack.append(tok)
            elif tok.nodeName == ')':
                while len(stack) > 0:
                    if not isinstance(stack[-1], number) and stack[-1].nodeName == '(':
                        break
                    postfix.append(stack.pop())
                stack.pop()  # (
            else:
                # Handle operators and precedence
                while len(stack) > 0 and self.prec(tok) <= self.prec(stack[-1]):
                    postfix.append(stack.pop())
                stack.append(tok)
        while len(stack) > 0:
            postfix.append(stack.pop())

        # Now evaluate the expression in postfix form
        while len(postfix) > 0:
            tok = postfix.pop(0)
            if isinstance(tok, _boolToken):
                stack.append(tok)
            elif isinstance(tok, number):
                stack.append(tok)
            elif isinstance(tok, _and) or isinstance(tok, AND):
                op1 = stack.pop()
                op2 = stack.pop()
                if isinstance(op1, _boolToken) and isinstance(op2, _boolToken):
                    stack.append(_true() if op1.state and op2.state else _false())
                else:
                    raise ValueError('Missing expected boolean value')
            elif isinstance(tok, _or) or isinstance(tok, OR):
                op1 = stack.pop()
                op2 = stack.pop()
                if isinstance(op1, _boolToken) and isinstance(op2, _boolToken):
                    stack.append(_true() if op1.state or op2.state else _false())
                else:
                    raise ValueError('Missing expected boolean value')
            elif isinstance(tok, _not) or isinstance(tok, NOT):
                op1 = stack.pop()
                if isinstance(op1, _boolToken):
                    stack.append(_false() if op1.state else _true())
                else:
                    raise ValueError('Missing expected boolean value')
            elif tok == '>':
                op2 = stack.pop()
                op1 = stack.pop()
                if isinstance(op1, number) and isinstance(op2, number):
                    stack.append(_true() if op1 > op2 else _false())
                else:
                    raise ValueError('Missing expected number')
            elif tok == '<':
                op2 = stack.pop()
                op1 = stack.pop()
                if isinstance(op1, number) and isinstance(op2, number):
                    stack.append(_true() if op1 < op2 else _false())
                else:
                    raise ValueError('Missing expected number')
            elif tok == '=':
                op2 = stack.pop()
                op1 = stack.pop()
                if isinstance(op1, number) and isinstance(op2, number):
                    stack.append(_true() if op1 == op2 else _false())
                else:
                    raise ValueError('Missing expected number')

        if len(stack) > 0 and isinstance(stack[-1], _boolToken):
            return stack[-1]
        else:
            return _false()


class whiledo(ifthenelse):
    r"""The \whiledo macro.

    Similar to ifthenelse, but repeatedy append the second argument to the
    resulting expansion until the first argument expands and evaluates to false.
    """
    args = 'test:nox operations:nox'

    def invoke(self, tex) -> List[Token]:
        a = self.parse(tex)
        tok: List[Token] = []
        while True:
            expanded = tex.expandTokens(a['test'], parentNode=self.parentNode)
            if isinstance(expanded, TeXFragment):
                test_result = self.evaluate(tex, expanded)
            else:
                test_result = self.evaluate(tex, [expanded])
            if not test_result.state:
                break
            tok += tex.expandTokens(a['operations'], parentNode=self.parentNode)
        return tok


class boolean(Command):
    """Expand to a _boolToken depending on the value of the named TeX if"""
    args = 'name:str'

    def invoke(self, tex):
        a = self.parse(tex)
        if a['name'] in self.ownerDocument.context.keys():
            if self.ownerDocument.context[a['name']].state:
                return [_true()]
            else:
                return [_false()]


class isodd(Command):
    """Expand to a _boolToken, _true if the provided number is odd"""
    args = 'number:int'

    def invoke(self, tex):
        a = self.parse(tex)
        if a['number'] is not None and a['number'] % 2 == 1:
            return [_true()]
        else:
            return [_false()]


class equal(Command):
    """Expand to a _boolToken, _true if arguments expand to the same string"""
    args = 'first:str second:str'

    def invoke(self, tex):
        a = self.parse(tex)
        if a['first'] == a['second']:
            return [_true()]
        else:
            return [_false()]


class isundefined(Command):
    """Expand to a _boolToken, _true if the argument is not defined"""
    args = 'name:cs'

    def invoke(self, tex):
        a = self.parse(tex)
        if a['name'] in self.ownerDocument.context.keys():
            return [_false()]
        else:
            return [_true()]


class lengthtest(Command):
    """Evaluate a length test and return a _boolToken depending on the result"""
    args = 'test:nox'

    def invoke(self, tex):
        attr = self.parse(tex)
        test = attr['test']
        tex.pushTokens(test)
        a = tex.readDimen()
        relation = next(tex.itertokens())
        b = tex.readDimen()
        if relation == '<':
            if a < b:
                return [_true()]
            else:
                return [_false()]
        elif relation == '>':
            if a > b:
                return [_true()]
            else:
                return [_false()]
        elif relation == '=':
            if abs(a - b) < 1e-6:
                return [_true()]
            else:
                return [_false()]
        raise ValueError('"%s" is not a valid relation' % relation)


class newboolean(Command):
    """Create a new TeX if with the provided name"""
    args = 'name:str'

    def invoke(self, tex):
        self.ownerDocument.context.newif(self.parse(tex)['name'])


class provideboolean(newboolean):
    pass


class setboolean(Command):
    """Set the value of the named TeX if"""
    args = 'name:str value:str'

    def invoke(self, tex):
        a = self.parse(tex)
        if a['name'] in self.ownerDocument.context.keys():
            if a['value'].lower() == 'true':
                self.ownerDocument.context[a['name']].setTrue()
            elif a['value'].lower() == 'false':
                self.ownerDocument.context[a['name']].setFalse()
        else:
            raise ValueError("Boolean %s not defined" % a['name'])
