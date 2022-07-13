from plasTeX.PackageResource import (PackageTemplateDir)
from plasTeX import Command, Environment
from plasTeX.Base.LaTeX.Lists import List


def ProcessOptions(options, document):
    context = document.context
    context.newcounter('question')
    context['theenumi'].format = '${thesect}${thequestion}(${enumi.alph})'
    context['theenumii'].format = '${theenumi}(${enumii.roman})'
    context['theenumiii'].format = '${theenumii}${enumii.Alph}.'

    document.userdata['variant'] = 1
    document.userdata['modulecodes'] = {0: 'MAS0000', 1: 'MAS0000', 2: 'MAS0000', 3: 'MAS0000', 4: 'MAS0000'}
    document.userdata['submarks'] = 0
    document.userdata['calculatorpermitted'] = True
    document.userdata['examyear'] = ''
    document.userdata['semestertext'] = ''
    document.userdata['sectlet'] = ''
    document.userdata['sectsep'] = ''

    tpl = PackageTemplateDir(renderers='html5', package='nclexam')
    document.addPackageResource([tpl])


class question(Environment):
    args = 'num_v1:str { num_v2:str } { num_v3:str } { num_v4:str }'
    counter = 'question'

    def invoke(self, tex):
        Command.invoke(self, tex)
        self.section = self.ownerDocument.userdata['sectlet'] + self.ownerDocument.userdata['sectsep']

    def postParse(self, tex):
        res = Environment.postParse(self, tex)
        var = self.ownerDocument.userdata['variant']
        self.variantMarkString = 'num_v%d' % var

        while not self.attributes[self.variantMarkString]:
            var = var - 1
            self.variantMarkString = 'num_v%d' % var

        try:
            self.mark = int(self.attributes[self.variantMarkString])
            self.markText = "%d mark" % self.mark
            if self.mark != 1:
                self.markText += "s"
        except Exception:
            self.hidden = True
            self.ownerDocument.context.counters['question'].value -= 1
        return res


class solution(Command):
    args = '* [ height ] solution'

    def invoke(self, tex):
        Command.invoke(self, tex)
        self.solution = self.attributes['solution']
        self.star = self.attributes['*modifier*'] == '*'


class setvariant(Command):
    args = 'var:int'

    def invoke(self, tex):
        Command.invoke(self, tex)
        self.ownerDocument.userdata['variant'] = self.attributes['var']


class modulename(Command):
    args = 'modulename:str'

    def invoke(self, tex):
        Command.invoke(self, tex)
        self.ownerDocument.userdata['modulename'] = self.attributes['modulename']


class semester(Command):
    args = 'semestertext:str'

    def invoke(self, tex):
        Command.invoke(self, tex)
        if self.attributes['semestertext'] == '1':
            self.ownerDocument.userdata['semestertext'] = "Semester 1"
        elif self.attributes['semestertext'] == '2':
            self.ownerDocument.userdata['semestertext'] = "Semester 2"
        else:
            self.ownerDocument.userdata['semestertext'] = self.attributes['semestertext']


class setyear(Command):
    args = 'examyear:str'

    def invoke(self, tex):
        Command.invoke(self, tex)
        self.ownerDocument.userdata['examyear'] = self.attributes['examyear']


class settime(Command):
    args = 'examtime:str'

    def invoke(self, tex):
        Command.invoke(self, tex)
        self.ownerDocument.userdata['examtime'] = self.attributes['examtime']


class extrainstructions(Command):
    args = 'extrainstructions:str'

    def invoke(self, tex):
        Command.invoke(self, tex)
        self.ownerDocument.userdata['extrainstructions'] = self.attributes['extrainstructions']


class calculatorpermitted(Command):
    args = 'calculatorpermitted:str'

    def invoke(self, tex):
        Command.invoke(self, tex)
        if self.attributes['calculatorpermitted'] == "true":
            self.ownerDocument.userdata['calculatorpermitted'] = True
        else:
            self.ownerDocument.userdata['calculatorpermitted'] = False


class solutionshow(Command):
    args = 'solshow:str'

    def invoke(self, tex):
        Command.invoke(self, tex)
        if self.attributes['solshow'] == "full":
            self.ownerDocument.userdata['solshow'] = True
        else:
            self.ownerDocument.userdata['solshow'] = False


class moduleno(Command):
    args = '[ var:int ] code:str'

    def invoke(self, tex):
        Command.invoke(self, tex)

        if self.attributes['var']:
            self.ownerDocument.userdata['modulecodes'][self.attributes['var']] = self.attributes['code']
        else:
            self.ownerDocument.userdata['modulecodes'][1] = self.attributes['code']


class comment(Command):
    args = 'comment'

    def invoke(self, tex):
        Command.invoke(self, tex)
        self.comment = self.attributes['comment']


class submarks(Command):
    args = 'num_v1:str { num_v2:str } { num_v3:str } { num_v4:str }'

    def invoke(self, tex):
        Command.invoke(self, tex)
        var = self.ownerDocument.userdata['variant']
        self.variantMarkString = 'num_v%d' % var
        while not self.attributes[self.variantMarkString]:
            var = var - 1
            self.variantMarkString = 'num_v%d' % var
        try:
            self.mark = int(self.attributes[self.variantMarkString])
            self.markText = "%d mark" % self.mark
            if self.mark != 1:
                self.markText += "s"
        except Exception:
            pass


class sect(Command):
    args = '[sep:str] sectlet:str'

    def invoke(self, tex):
        Command.invoke(self, tex)
        self.ownerDocument.userdata['sectlet'] = self.attributes['sectlet'] or ''
        self.ownerDocument.userdata['sectsep'] = self.attributes['sep'] or ''
        self.section = self.ownerDocument.userdata['sectlet'] + self.ownerDocument.userdata['sectsep']
        self.ownerDocument.context.newcommand('thesect', 0, self.section)


class makefront(Command):
    args = ''

    def invoke(self, tex):
        self.modulecode = self.ownerDocument.userdata['modulecodes'][self.ownerDocument.userdata['variant']]


class theend(Command):
    args = '[str]'


class List(List):
    class item(List.item):
        def invoke(self, tex):
            """ Set up counter for this list depth """
            try:
                self.counter = List.counters[List.depth - 1]
                self.position = self.ownerDocument.context.counters[self.counter].value + 1
            except (KeyError, IndexError):
                pass
            res = Command.invoke(self, tex)
            if self.attributes['term'] == '':
                self.attributes['term'] = ' '
            return res

        def postArgument(self, arg, value, tex):
            res = Command.postArgument(self, arg, value, tex)
            self.alph = self.ownerDocument.context.counters[self.counter].alph
            self.roman = self.ownerDocument.context.counters[self.counter].roman
            self.Alph = self.ownerDocument.context.counters[self.counter].Alph
            return res


class enumerate_(List):
    macroName = 'enumerate'
    args = '[ type ]'


class itemize(List):
    pass
