class JSONSerializable(object):
    _json_attrs = []

    def to_dict(self):
        return dict((attr, getattr(self, attr)) for attr in self._json_attrs)

    def to_json(self):
        return JSONEncoder().encode(self.to_dict())

    @classmethod
    def from_dict(cls, d):
        obj = cls()
        for k,v in d.iteritems():
            setattr(obj, k, v)
        return obj
