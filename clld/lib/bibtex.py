class Record(dict):

    def __init__(self, genre, id, **kwargs):
        self.genre = genre
        self.id = id
        dict.__init__(self, kwargs)

    def serialize(self):
        fields = []
        m = max([0] + list(map(len, self.keys())))

        for k in sorted(self.keys()):
            values = self[k]
            if not isinstance(values, (tuple, list)):
                values = [values]
            fields.append("  %s = {%s}," % (k.ljust(m), " and ".join(filter(None, values))))

        return """@%s{%s,
%s
}
""" % (self.genre, self.id, "\n".join(fields)[:-1])  # remove the comma after the last field entry
