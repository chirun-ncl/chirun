from plasTeX import Environment
from plasTeX import encoding
from plasTeX.Base.LaTeX import Lists
from plasTeX.Logging import getLogger
import re

log = getLogger()


class List(Lists.List):
    def digest(self, tokens):
        if self.macroMode != Environment.MODE_END:
            # Drop any whitespace before the first item
            for tok in tokens:
                if tok.isElementContentWhitespace:
                    continue
                elif tok.nodeName == 'itemsep':
                    tok.digest([])
                    continue
                elif tok.nodeName == 'setcounter':
                    tok.digest([])
                    continue
                if tok.nodeName != 'item':
                    log.warning('dropping non-item from beginning of list')
                    continue
                tokens.push(tok)
                break
        Environment.digest(self, tokens)


Lists.List = List


class description(List):
    pass


class trivlist(List):
    pass


class itemize(List):
    pass


class ConfigurableList(List):
    macroName = 'list'
    args = 'defaultlabel decls:nox'


def numToRoman(x: int) -> str:
    n, number = divmod(x, 1000)
    roman = "M" * n
    if number >= 900:
        roman = roman + "CM"
        number = number - 900
    while number >= 500:
        roman = roman + "D"
        number = number - 500
    if number >= 400:
        roman = roman + "CD"
        number = number - 400
    while number >= 100:
        roman = roman + "C"
        number = number - 100
    if number >= 90:
        roman = roman + "XC"
        number = number - 90
    while number >= 50:
        roman = roman + "L"
        number = number - 50
    if number >= 40:
        roman = roman + "XL"
        number = number - 40
    while number >= 10:
        roman = roman + "X"
        number = number - 10
    if number >= 9:
        roman = roman + "IX"
        number = number - 9
    while number >= 5:
        roman = roman + "V"
        number = number - 5
    if number >= 4:
        roman = roman + "IV"
        number = number - 4
    while number > 0:
        roman = roman + "I"
        number = number - 1
    return roman


class enumerate_(List):
    macroName = 'enumerate'
    args = '[ type:str ]'

    def term(self, position):
        alph = encoding.stringletters()[position - 1]
        if self.listType:
            t = re.sub(r'(?<!{)I(?!})', numToRoman(position), self.listType)
            t = re.sub(r'(?<!{)i(?!})', numToRoman(position).lower(), t)
            t = re.sub(r'(?<!{)1(?!})', str(position), t)
            t = re.sub(r'(?<!{)A(?!})', alph.upper(), t)
            t = re.sub(r'(?<!{)a(?!})', alph.lower(), t)
        elif self.listDepth == 2:
            t = '({})'.format(alph.lower())
        elif self.listDepth == 3:
            t = '{}.'.format(numToRoman(position).lower())
        elif self.listDepth == 4:
            t = '{}.'.format(alph.upper())
        else:
            t = '{}.'.format(position)
        return t

    def invoke(self, tex):
        Lists.List.invoke(self, tex)
        self.listType = None
        if 'type' in self.attributes:
            self.listType = self.attributes['type']
        self.listDepth = Lists.List.depth
