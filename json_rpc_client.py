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
