


class contingacy_table(object):
    def __init__(self, data, atts):
        data=data
        self.atts=atts
        self.groups = data.groupby[atts].count()


    def get_marginals(self,x,y):
        atts=self.att.copy()
        for item in x:
            atts.remove(item)
        for item in y:
            atts.remove(item)