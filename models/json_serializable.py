class JSONSerializable(object):
    _json_attrs = []
    def __init__(self, d):
        self.from_dict(d)

    def to_dict(self):
        return dict((attr, getattr(self, attr)) for attr in self._json_attrs)

    def to_json(self):
        return JSONEncoder().encode(self.to_dict())

    @classmethod
    def from_dict(cls, d):
        obj = cls()
        obj.from_dict(d)
        return obj

    def from_dict(self, d):
        for k,v in d.iteritems():
            setattr(obj, k, v)
