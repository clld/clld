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
