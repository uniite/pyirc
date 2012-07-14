from json_serializable import JSONSerializable




class NumberOrText(JSONSerializable):
    _json_attrs = ["number", "text"]
    def __init__(self, value=None):
        # Number
        if hasattr(value, "__div__"):
            self.number = value
            self.text = None
        # Text
        else:
            self.number = None
            self.text = value
    def value(self):
        return self.number or self.text


class Delta(JSONSerializable):
    _json_attrs = ["target", "event", "dataType"]

    def __init__(self, target=None, event=None, data=None):
        self.target = [NumberOrText(x) for x in target]
        self.event = event
        self.data = data

    def __setattr__(self, key, value):
        if key == "target":
            value = self.decode_target(value)
        elif key == "data":
            self.dataType = value.__class__.__name__
        super(self.__class__, self).__setattr__(key, value)

    @classmethod
    def decode_target(cls, t):
        return [NumberOrText(x).value() for x in t]
