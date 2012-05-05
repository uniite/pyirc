from json_serializable import JSONSerializable


class Message(JSONSerializable):
    _json_attrs = ["id", "sender", "body"]
    def __init__(self, id, sender, body, conversation=None):
        self.id = id
        self.sender = str(sender)
        self.body = str(body)
        self.conversation = conversation

    def __str__(self):
        short_msg = self.body
        if len(short_msg) > 15:
            short_msg = short_msg[:15] + "..."
        return "<Message(sender=%s, body=%s, conversation=%s>" % (
            repr(self.sender),
            repr(short_msg),
            repr(self.conversation)
            )
