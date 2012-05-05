from json_serializable import JSONSerializable
from observable import SimpleObservable, ObservableList


class Conversation(JSONSerializable, SimpleObservable):
    _json_attrs = ["name", "topic", "messages", "users", "index"]
    def __init__(self, name, connection, users=None):
        SimpleObservable.__init__(self)
        self.name = name
        self.connection = connection
        self.users = users or []
        self.users = ObservableList(*users)
        self.topic = ""
        self.messages = ObservableList()
        self.index = None
        #self.messages.subscribe("add", self.new_message)
        #self.messages.subscribe("remove", self.delete_message)

    def recv_message(self, message):
        message.id = len(self.messages)
        self.messages.append(message)

    def send_message(self, message):
        message.id = len(self.messages)
        self.messages.append(message)
        self.connection.send_message(message)

    def delete_message(self, index, message):
        raise Exception("Message deletion not allowed!")


class DiffGenerator(object):
    def callback(self, event, *args, **kwargs):
        if event == "add":
            pass
