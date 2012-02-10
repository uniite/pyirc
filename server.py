#! /usr/bin/env python
import gevent.monkey
gevent.monkey.patch_all()

from gevent import Greenlet
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
    _json_attrs = ["name", "topic", "messages"]
    def __init__(self, name, connection, users=None):
        SimpleObservable.__init__(self)
        self.name = name
        self.connection = connection
        self.users = users or {}
        self.topic = ""
        self.messages = ObservableList()
        #self.messages.subscribe("add", self.new_message)
        #self.messages.subscribe("remove", self.delete_message)

    def new_message(self, message):
        print "[Conv:%s] %s" % (self.name, message)

    def delete_message(self, index, message):
        raise Exception("Message deletion not allowed!")


class DiffGenerator(object):
    def callback(self, event, *args, **kwargs):
        if event == "add":
            pass

class Session(SimpleObservable, JSONSerializable):
    _json_attrs = ["conversations"]
    def __init__(self):
        self.connections = {} #ObservableDict()
        self.users = {} #ObservableDict()
        self.conversations = ObservableList()
        self.conversation_lookup = {}

    def get_conversation(self, key):
        if self.conversations.has_key(key):
            return self.conversations[key]
        else:
            return None

    def recv_message(self, connection, username, message, chatroom=None):
        if chatroom:
            conv_name = chatroom

        else:
            conv_name = username
        conv_key = "%s@%s" % (conv_name, connection)
        conv = self.conversation_lookup.get(conv_key)
        if not conv:
            conv = Conversation(conv_name, connection, {})
            self.conversations.append(conv)
            self.conversation_lookup[conv_key] = conv
        conv.messages.append(Message(len(conv.messages), username, message, conv))

    def start(self):
        irc = IRCConnection(self, [("irc.freenode.org", 6667)], "pyguybot", "pyguybot")
        self.connections["irc"] = irc
        print "Connecting..."
        irc.start()


def main():
    session = Session()
    session_greenlet = Greenlet.spawn(session.start)
    session_greenlet.join()

if __name__ == "__main__":
    main()