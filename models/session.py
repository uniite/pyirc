from json_serializable import JSONSerializable
from irc_connection import IRCConnection
from models import Conversation, Message
from observable import ObservableList, SimpleObservable


class Session(SimpleObservable, JSONSerializable):
    _json_attrs = ["conversations", "users"]
    def __init__(self):
        self.connections = {} #ObservableDict()
        self.users = ObservableList()
        self.conversations = ObservableList()
        self.conversation_lookup = {}

    def conversation_key(self, connection, name):
        return "%s@%s" % (name, connection)

    def get_conversation(self, connection, name):
        return self.conversation_lookup.get(self.conversation_key(connection, name))

    def new_conversation(self, connection, name):
        conv = Conversation(name, connection, {})
        conv.index = len(self.conversations)
        self.conversations.append(conv)
        self.conversation_lookup[self.conversation_key(connection, name)] = conv
        self.last_key = self.conversation_key(connection, name)
        return conv

    def leave_conversation(self, connection, name):
        for i in range(len(self.conversations)):
            c = self.conversations[i]
            print c
            if c.name == name and c.connection == connection:
                print "DELETED"
                del self.conversations[i]
                break

    def user_joined_conversation(self, connection, username, chatroom):
        self.get_conversation(connection, chatroom).users.append(username)

    def user_left_conversation(self, connection, username, chatroom):
        try:
            self.get_conversation(connection, chatroom).users.remove(username)
        except:
            print "Failed to remove %s from %s" % (username, self.get_conversation(connection, chatroom))


    def recv_message(self, connection, username, message, chatroom=None):
        if chatroom:
            conv_name = chatroom
        else:
            conv_name = username
        conv = self.get_conversation(connection, conv_name)
        if not conv:
            conv = self.create_conversation(connection, conv_name)
        conv.recv_message(Message(None, username, message, conv))

    def send_message(self, conversation_id, message):
        conv = self.conversations[conversation_id]
        conv.send_message(Message(None, "me", message, conv))
        # TODO: Support IRC ['ACTION', 'looks around']
    def start(self):
        irc = IRCConnection(self, [("irc.freenode.org", 6667)], "python_phone", "python_phone")
        self.connections["irc"] = irc
        print "Connecting..."
        irc.start()
        print "Connected."
