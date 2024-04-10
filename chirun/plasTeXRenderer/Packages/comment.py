from plasTeX import VerbatimEnvironment


class comment(VerbatimEnvironment):
    def invoke(self, tex):
        VerbatimEnvironment.invoke(self, tex)
        return []
