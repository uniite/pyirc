#! /usr/bin/env python

# BUGS
# - Subscription.cancel on ws_server fails
# - Message body: UnicodeDecodeError: 'utf8' codec can't decode byte 0x95 in position 0: invalid start byte

import gevent.monkey
gevent.monkey.patch_all()

from gevent import Greenlet, sleep
from irc_connection import IRCConnection
from observable import SimpleObservable, ObservableList, ObservableDict

import json



class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, "to_dict"):
            return o.to_dict()
        else:
            json.JSONEncoder(self, o)

class JSONSerializable(object):
    _json_attrs = []
    def to_dict(self):
        return dict((attr, getattr(self, attr)) for attr in self._json_attrs)

    def to_json(self):
        return JSONEncoder().encode(self.to_dict())


class User(JSONSerializable):
    _json_attrs = ["name", "alias", "connection"]
    def __init__(self, name, alias="", connection=None):
        self.name = name
        self.alias = alias
        self.connection = connection

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

    def new_conversation(self, name, connection):
        conv = Conversation(name, connection, {})
        conv.index = len(self.conversations)
        self.conversations.append(conv)
        self.conversation_lookup[self.conversation_key(connection, name)] = conv
        self.last_key = self.conversation_key(connection, name)
        return conv

    def user_joined_conversation(self, connection, username, chatroom):
        self.get_conversation(connection, chatroom).users.append(username)

    def user_left_conversation(self, connection, username, chatroom):
        self.get_conversation(connection, chatroom).users.remove(username)


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

    def start(self):
        irc = IRCConnection(self, [("irc.freenode.org", 6667)], "python_phone", "python_phone")
        self.connections["irc"] = irc
        print "Connecting..."
        irc.start()

def spam(session):
    i = 0
    while True:
        i += 1
        session.recv_message({}, "spambot", "SPAM %s" % i, "testchat")
        sleep(0.05)

def main():
    session = Session()
    session_greenlet = Greenlet.spawn(session.start)
    spam_greenlet.join()

if __name__ == "__main__":
    main()