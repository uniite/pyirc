import os
from gevent import Greenlet, sleep
from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket import WebSocketHandler
import json
from server import Session, JSONEncoder


class RPCService(object):
    @classmethod
    def listMethods(cls):
        return ["getConversations", "getMessages", "shout", "getSession"]

    @classmethod
    def getConversations(cls):
        return session.conversations.values()

    @classmethod
    def getSession(cls):
        return session.to_dict()

    @classmethod
    def getMessages(cls):
        messages = []
        for conv in session.conversations.values():
            messages.extend(conv.messages)
        return messages

    @classmethod
    def shout(cls, name):
        return "HEY %s!" % name

def rpc_server(environ, start_response):
    websocket = environ.get("wsgi.websocket")
    if websocket is None:
        return http_handler(environ, start_response)
    try:
        print "Got websocket request"
        def on_event(target, event, data):
            delta = {
                "event": event,
                "target": target,
                "data": data
            }
            print JSONEncoder().encode(delta)
            websocket.send(JSONEncoder().encode({"notification": {"delta": delta}}))
        subscription = session.subscribe("__all__", on_event)
        while True:
            request = websocket.receive()
            if request is None:
                break
            else:
                result = handle_json_rpc_request(request)
                if result:
                    websocket.send(result)
    except WebSocketError, ex:
        print "%s: %s" % (ex.__class__.__name__, ex)
    finally:
        subscription.cancel()
        websocket.close()

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
        # Raise an exception if the method name is invalid
        if not hasattr(RPCService, request["method"]) or request["method"].startswith("_"):
            raise Exception("Method '%s' not found", )
        # Get the method
        method = getattr(RPCService, request["method"])
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






def main():
    global session
    session = Session()
    session_greenlet = Greenlet.spawn(session.start)
    WSGIServer(("", 8000), rpc_server, handler_class=WebSocketHandler).serve_forever()

if __name__ == "__main__":
    main()

