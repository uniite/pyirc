import gevent.monkey; gevent.monkey.patch_all()
from gevent import Greenlet, sleep
from gevent.server import StreamServer
import json
from models import Message, Session, JSONEncoder, JSONSerializable
from struct import pack, unpack
import traceback

from models.client_session import ClientSession


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
    print "Got connection"
    client_session = ClientSession(socket, session)






def main():
    global session
    session = Session()
    irc = Greenlet.spawn(session.start)
    server = StreamServer(("", 35421), handle)
    server.serve_forever()

if __name__ == "__main__":
    main()

