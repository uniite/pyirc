import json
from struct import pack, unpack
import traceback

from observable import Subscription
from delta import Delta
from json_encoder import JSONEncoder

import controllers




def pack_data(data):
    return pack("!I", len(data)) + data


class ClientSession(object):
    def __init__(self, socket, server_session):
        try:
            self.server_session = server_session
            self.socket = socket
            self.subscriptions = {}
            self.current_conversation_id = None

            print "Got TCP connection"
            #send_obj(RPCService.getMessages())
            self.server_subscription = server_session.subscribe("__all__", self.handle_event)
            for c in server_session.conversations:
                delta = Delta(("conversations", -1), "add")
                delta.data = c
                self.send_obj(delta)
                self.send_obj(c)

            while True:
                request = self.recv_obj()
                print "Got request: %s" % request
                if request is None:
                    break
                else:
                    self.handle_request(request)
        except Exception, e:
            print "Error: %s" % e
            print traceback.format_exc()

    def recv_obj(self):
        try:
            s = self.socket.recv(4)
            print len(s)
            size = unpack("!I", s)[0]
            print "Got size: %s" % size
            return json.loads(self.socket.recv(size))
        except Exception:
            print "Recv error!"
            print traceback.format_exc()
            return None

    def handle_request(self, request):
        if type(request) == list:
            for r in request:
                self.handle_request(r)
        else:
            print "Parsing request: %s" % request
            try:
                controller = getattr(controllers, request["controller"])
                action = getattr(controller, request["action"])
                args = request["args"] or []
                if "kwargs" in request:
                    kwargs = request["kwargs"]
                else:
                    kwargs = {}
                print "%s#%s => %s, %s" % (controller, action, args, kwargs)
            except AttributeError, e:
                print "Bad Request (AttributeError: %s)" % e.args
                return False
            except KeyError, e:
                print "Bad Request (KeyError: %s)" % e.args
                return False

            return action(self, *args, **kwargs)

    def handle_event(self, target, event, data):
        # We only want to send down:
        # - Conversations (add/remove)
        # - Basic info about Conversations (change)
        # - Messages in the current Conversation (add)
        print "Event: %s, %s, %s" % (target, event, data)
        delta_target = None
        if target[0] == "conversations":
            conv_id = target[1]
            # Add/Remove a Conversation
            if len(target) == 2:
                delta_target = target
            # Something changed under a Conversation
            else:
                field = target[2]
                print "Field: %s" % field
                if field == "unread_count":
                    delta_target = target
                # We only care about these for the current Conversation
                elif conv_id == self.current_conversation_id:
                    # Add a Message
                    if field == "messages" and event == "add":
                        delta_target = ["messages", -1]

        # Ignore data we don't want to send down
        if delta_target:
            # Put together a delta the client can decode easily
            delta = Delta(delta_target, event, data)
            # and send it down
            self.send_obj(delta)
            self.send_obj(data)
            return True
        else:
            return False


    def send_obj(self, obj):
        try:
            self.socket.send(
                pack_data(obj.__class__.__name__) +
                pack_data(JSONEncoder().encode(obj)))
            print "Sent %s" % JSONEncoder().encode(obj)
            return True
        except Exception:
            print "Send error!"
            print traceback.format_exc()
            return False

    def join_conversation(self, name):
        conn = self.server_session.connections.values()[0].connection
        return self.server_session.join_conversation(conn, name)

    def leave_conversation(self, name):
        conn = self.server_session.connections.values()[0].connection
        return self.server_session.leave_conversation(conn, name)

    def send_message(self, conversation_id, message_body):
        return self.server_session.send_message(conversation_id, message_body)

    def on_delta(self, delta):
        print "Target: %s" % delta.target
        if delta.target[0] == "conversations":
            if delta.event == "add":
                conv = self.recv_obj()
                print "Got conversation: %s" % conv
                self.session.connections.values()[0].connection.join(conv["name"])
            elif delta.event == "remove":
                conv = self.recv_obj()
                print "Got conversation: %s" % conv
                self.server_session.connections.values()[0]\
                    .connection.part([conv["name"]])

    def subscribe(self, observable, event, prefix):
        Subscription(self.handle_event, observable, event, True, prefix)

    def unsubscribe(self, sid):
        if sid in self.subscriptions:
            self.subscriptions[sid].cancel()
            del self.subscriptions[sid]
            return True
        else:
            return False
