from plasTeX.Base.LaTeX.Characters import ding

from plasTeX.Base.LaTeX.Lists import List

class dinglist(List):
    args = 'ding:int'

    def symbol(self):
        return ding.values.get(self.attributes['ding'])
