#! /usr/bin/env python
import gevent.monkey
gevent.monkey.patch_all()

from gevent import Greenlet, sleep
from irc_connection import IRCConnection

import json
import collections

import time


class SimpleObservable(object):
    def _notify(self, event, *args, **kwargs):
        if hasattr(self, "_subscribers") and self._subscribers.has_key(event):
            self._subscribers[event](*args, **kwargs)

    def subscribe(self, event, callback):
        if not hasattr(self, "_subscribers"):
            self._subscribers = {}
        self._subscribers[event] = callback



class ObservableList(collections.MutableSequence, SimpleObservable):

    def __init__(self, *args):
        self.list = list()
        self.extend(list(args))

    def __len__(self): return len(self.list)

    def __getitem__(self, i): return self.list[i]

    def __delitem__(self, i):
        self._notify("remove", i, self.list[i])
        del self.list[i]

    def __setitem__(self, i, v):
        self.list[i] = v

    def insert(self, i, v):
        self._notify("add", v)
        self.list.insert(i, v)

    def __str__(self):
        return str(self.list)

    def to_dict(self):
        return self.list



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

class Conversation(JSONSerializable):
    _json_attrs = ["name", "topic", "messages"]
    def __init__(self, name, connection, users={}):
        self.name = name
        self.connection = connection
        self.users = users
        self.topic = ""
        self.messages = ObservableList()
        self.messages.subscribe("add", self.new_message)
        self.messages.subscribe("remove", self.delete_message)

    def new_message(self, message):
        print "[Conv:%s] %s" % (self.name, message)

    def delete_message(self, index, message):
        raise Exception("Message deletion not allowed!")

class Session(object):
    connections = {}
    users = {}
    conversations = {}

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
        conv_key = (connection, conv_name)
        conv = self.conversations.get(conv_key)
        if not conv:
            conv = Conversation(conv_name, connection, {})
            self.conversations[conv_key] = (conv)
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