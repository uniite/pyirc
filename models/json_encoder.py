import json


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, "to_dict"):
            return o.to_dict()
        else:
            json.JSONEncoder(self, o)
