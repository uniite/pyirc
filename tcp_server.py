import os
import gevent
from gevent import Greenlet, sleep
from gevent.server import StreamServer
import json
from models import Message, Session, JSONEncoder, JSONSerializable
from struct import pack, unpack
from json_rpc_client import handle_json_rpc_request
import traceback

from models.client_session import ClientSession
from models.rpc_service import RPCService


def recv_obj(socket):
    try:
        s = socket.recv(4)
        print len(s)
        size = unpack("!I", s)[0]
        print "Got size: %s" % size
        return json.loads(socket.recv(size))
    except:
        print "Recv error!"
        print traceback.format_exc()
        return None


def pack_data(data):
    return pack("!I", len(data)) + data

def send_obj(socket, obj):
    try:
        socket.send(
            pack_data(obj.__class__.__name__) +
            pack_data(JSONEncoder().encode(obj)))
        print "Sent %s" % JSONEncoder().encode(obj)
        return True
    except:
        print "Send error!"
        print traceback.format_exc()
        return False


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
    def __setattr__(self, key, value):
        if key == "target":
            value = decode_target(value)
        elif key == "data":
            self.dataType = data.__class__.__name__
        super(object, self).__setattr__(self, key, value)

def decode_target(t):
    return [NumberOrText.from_dict(x).value() for x in t]

class Subscription(JSONSerializable):
    _json_attrs = ["target"]
    def __setattr__(self, key, value):
        if key == "target":
            value = decode_target(value)
        super(object, self).__setattr__(self, key, value)

def handle(socket, address):
    try:
        print "Got TCP connection"
        #send_obj(RPCService.getMessages())
        filters = ["conversations", "messages"]
        def on_event(target, event, data):
            # We only want to operate one-level deep
            # (usually on lists)
            target = list(target)[-2:]
            # Put together a delta the client can decode easily
            delta = Delta(target, event, data)
            if target[0] in filters:
                send_obj(socket, delta)
                send_obj(socket, data)
        #subscription = session.conversations[0].subscribe("messages", on_msg)
        subscription = session.subscribe("__all__", on_event)
        for c in session.conversations:
            delta = Delta(("conversations", -1), "add", c)
            send_obj(socket, delta)
            send_obj(socket, c)
        while True:
            req = recv_obj(socket)
            print "Got request: %s" % req
            if req == None:
                break
            # Push Subscription
            if req.has_key("dataType"):
                target = [NumberOrText.from_dict(x).value() for x in req["target"]]
                filters.append(target)
            # Delta
            elif req.has_key("target"):
                target = [NumberOrText.from_dict(x).value() for x in req["target"]]
                print "Target: %s" % target
                if target[0] == "conversations":
                    if req["event"] == "add":
                        conv = recv_obj(socket)
                        print "Got conversation: %s" % conv
                        session.connections.values()[0].connection.join(conv["name"])
                    elif req["event"] == "remove":
                        conv = recv_obj(socket)
                        print "Got conversation: %s" % conv
                        session.connections.values()[0].connection.part([conv["name"]])
    except Exception, e:
        print "Error: %s" % e
        print traceback.format_exc()






def main():
    global session
    session = Session()
    irc = Greenlet.spawn(session.start)
    server = StreamServer(("", 35421), handle)
    server.serve_forever()

if __name__ == "__main__":
    main()

