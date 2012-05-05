from json_serializable import JSONSerializable


class User(JSONSerializable):
    _json_attrs = ["name", "alias", "connection"]
    def __init__(self, name, alias="", connection=None):
        self.name = name
        self.alias = alias
        self.connection = connection
