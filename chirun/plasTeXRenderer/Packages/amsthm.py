from plasTeX import Environment, Command


class swapnumbers(Command):
    pass


class theoremstyle(Command):
    args = 'style:str'


class newtheoremstyle(Command):
    args = 'name above below bodyfont indentamount headfont punctuation between headspec'


class newtheorem(Command):
    args = '* name:str [ shared:str ] header:str [ parent:str]'

    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        name = str(a['name'])
        header = a['header']
        star = a['*modifier*'] == '*'
        parent = a['parent']
        shared = a['shared']

        if star:
            counter = None
        else:
            if parent and not shared:
                self.ownerDocument.context.newcounter(name, initial=0, resetby=parent)
                self.ownerDocument.context.newcommand("the" + name, 0,
                                                      "\\arabic{%s}.\\arabic{%s}" % (parent, name))
                counter = name
            elif shared:
                counter = shared
            else:
                counter = name
                self.ownerDocument.context.newcounter(name, initial=0)
                self.ownerDocument.context.newcommand("the" + name, 0, "\\arabic{%s}" % name)

        data = {'nodeName': 'thmenv',
                'thmName': name,
                'args': '[title]',
                'counter': counter,
                'caption': header,
                'forcePars': True}
        th = type(name, (Environment,), data)
        self.ownerDocument.context.addGlobal(name, th)


class qedhere(Command):
    pass


class proof(Environment):
    blockType = True
    args = '[caption]'
    forcePars = True

    def digest(self, tokens):
        Environment.digest(self, tokens)
        self.caption = self.attributes.get('caption', '')
