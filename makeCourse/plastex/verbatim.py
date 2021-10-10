from makeCourse.plastex import VerbatimEnvironment


class verbatim(VerbatimEnvironment):
    pass


class comment(VerbatimEnvironment):
    def invoke(self, tex):
        VerbatimEnvironment.invoke(self, tex)
        return []
