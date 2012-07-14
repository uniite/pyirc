import os
import traceback

import gevent.monkey
# Monkey patching stdlib is not a necessity for all use cases
gevent.monkey.patch_all()
from gevent import Greenlet, sleep
from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket import WebSocketHandler
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import json
from tornado import web, ioloop
from sockjs.tornado import SockJSRouter, SockJSConnection

from models import JSONEncoder, RPCService
from server import Session, spam



class SessionConnection(SockJSConnection):
    def on_open(self, sockjs_session):
        print "Got websocket request"
        self.subscription = session.subscribe("__all__", self.on_event)

    def on_event(self, target, event, data):
        delta = {
            "event": event,
            "target": target,
            "data": data
        }
        print JSONEncoder().encode(delta)
        self.send(JSONEncoder().encode({"notification": {"delta": delta}}))

    def on_message(self, message):
        if message is not None:
            result = handle_json_rpc_request(message)
            if result:
                self.send(result)

    def on_close(self, sockjs_session):
        self.subscription.cancel()


def handle_json_rpc_request(request):
    # Parse the request
    try:
        request = json.loads(request)
        print request
    except:
        print "Ignoring malformed JSON-RPC request; could not parse as JSON: %s" % request
        return None

    # Validate the request object
    for key in ["id", "method", "params"]:
        if not request.has_key(key):
            print "Ignoring malformed JSON-RPC request; missing '%s'" % key
            return None

    # At this point, we can properly catch and respond with exceptions,
    # since we have a valid request id
    try:
        rpc_service = RPCService(session)
        # Raise an exception if the method name is invalid
        if not hasattr(rpc_service, request["method"]) or request["method"].startswith("_"):
            raise Exception("Method '%s' not found", )
        # Get the method
        method = getattr(rpc_service, request["method"])
        # Validate the parameters as a list of arguments,
        # with an optional dict of keyword arguments at the end
        args = request["params"]
        if not type(args) == list:
            raise Exception("Malformed JSON-RPC request parameters; not an array")
        if len(args) > 0 and type(args[-1]) == dict:
            kwargs = args.pop()
        else:
            kwargs = {}

        # Call the method with the given arguments, and store the result
        # If an exception occurs, the function-level except will handle it
        result = method(*args, **kwargs)
        print result
        exception = None

    # Handle all Exceptions as JSON-RPC exceptions
    except Exception, e:
        traceback.print_exc()
        result = None
        exception = {
            "name": "JSONRPCError",
            "code": 100,
            "message": e.message
        }

    # Return a JSON-RPC response containing the result or error
    response = {"id": request["id"], "result": result, "error": exception}
    return JSONEncoder().encode(response)

def http_handler(environ, start_response):
    if environ["PATH_INFO"].strip("/") == "version":
        start_response("200 OK", [])
        return [agent]
    else:
        start_response("400 Bad Request", [])
        return ["WebSocket connection is expected here."]




class IndexHandler(web.RequestHandler):
    def get(self):
        self.render('client/web/client3.html')

class GCMRegistrationHandler(web.RequestHandler):
    def post(self):
        reg_id = self.get_argument("regId")
        if reg_id:
            print "Got registration from %s: %s" % (self.request.remote_ip, reg_id)
            return "OK"
        else:
            print "No registration ID provided"
            return "Fail"

router = SockJSRouter(
    SessionConnection, "/session"
)

def main():
    global session
    session = Session()
    session_greenlet = Greenlet.spawn(session.start)
    #spam_greenlet = Greenlet.spawn(spam, session)
    http_server = HTTPServer(("", 8081), SimpleHTTPRequestHandler)
    http_greenlet = Greenlet.spawn(http_server.serve_forever)
    try:
        app = web.Application(
            router.urls +
            [("/", IndexHandler),
             ("/gcm/register", GCMRegistrationHandler),
             (r"/(.*)", web.StaticFileHandler, {"path": "client/web/"})],
            debug=True
        )
        app.listen(8000)
        print "Starting server on port 8000"
        loop = ioloop.IOLoop.instance().start()
        sockjs.serve_forever()
    except KeyboardInterrupt:
        sockjs.kill()





if __name__ == "__main__":
    main()

