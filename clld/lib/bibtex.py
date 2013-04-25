from collections import OrderedDict

from six import PY3


class Record(OrderedDict):

    def __init__(self, genre, id, *args, **kwargs):
        self.genre = genre
        self.id = id
        super(Record, self).__init__(args, **kwargs)

    def __unicode__(self):
        fields = []
        m = max([0] + list(map(len, self.keys())))

        for k in self.keys():
            values = self[k]
            if not isinstance(values, (tuple, list)):
                values = [values]
            fields.append(
                "  %s = {%s}," % (k.ljust(m), " and ".join(filter(None, values))))

        return """@%s{%s,
%s
}
""" % (self.genre, self.id, "\n".join(fields)[:-1])

    def __str__(self):
        """
        :return: a human readable label for the object, appropriately encoded (or not)
        """
        if PY3:
            return self.__unicode__()  # pragma: no cover
        return self.__unicode__().encode('utf-8')

    def text(self):
        res = ["%s (%s)" % (self.get('author', 'Anonymous'), self.get('year', 's.a.'))]
        if self.get('title'):
            res.append('"%s"' % self.get('title', ''))
        if self.get('editor'):
            res.append("in %s (ed)" % self.get('editor'))
        if self.get('booktitle'):
            res.append("%s" % self.get('booktitle'))
        for attr in ['school', 'journal', 'volume']:
            if self.get(attr):
                res.append(self.get(attr))
        if self.get('issue'):
            res.append("(%s)" % self['issue'])
        if self.get('pages'):
            res[-1] += '.'
            res.append("pp. %s" % self['pages'])
        if self.get('publisher'):
            res[-1] += '.'
            res.append("%s: %s" % (self.get('address', ''), self['publisher']))
        res[-1] += '.'
        return ' '.join(res)
