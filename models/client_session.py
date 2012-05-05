class ClientSession(object):
    def __init__(self, socket, server_session):
        self.server_session = server_session
        self.socket = socket

        print "Got TCP connection"
        #send_obj(RPCService.getMessages())
        self.server_subscription = server_session.subscribe("__all__", self.handle_event)
        for c in server_session.conversations:
            delta = Delta({
                "target": ("conversations", -1),
                "event": "add"
            })
            delta.data = c
            send_obj(socket, delta)
            send_obj(socket, c)

        while True:
            request = recv_obj(socket)
            print "Got request: %s" % req
            if request == None:
                break
            else:
                self.handle_request(request)

    def handle_request(self, request):
        if type(request) == list:
            for r in request:
                self.handle_request(r)
        else:
            handler = getattr(self, "on_" + {
                "d": "delta",
                "s": "subscribe",
                "u": "unsubscribe"
            }[request.keys[0]])
            self.request = request.values(0)
            hadnler()

    def handle_event(self, target, event, data):
        filters = ["conversations", "messages"]
        # We only want to operate one-level deep
        # (usually on lists)
        target = list(target)[-2:]
        # Put together a delta the client can decode easily
        delta = Delta(target, event, data)
        if target[0] in filters:
            send_obj(socket, delta)
            send_obj(socket, data)
            #subscription = session.conversations[0].subscribe("messages", on_msg)

    def on_delta(self):
        delta = Delta(self.request)
        print "Target: %s" % delta.target
        if delta.target[0] == "conversations":
            if delta.event == "add":
                conv = recv_obj(self.socket)
                print "Got conversation: %s" % conv
                session.connections.values()[0].connection.join(conv["name"])
            elif delta.event == "remove":
                conv = recv_obj(self.socket)
                print "Got conversation: %s" % conv
                session.connections.values()[0].connection.part([conv["name"]])
    def on_subscribe(self):
        subs = Subscription(self.request)
    def on_unsubscribe(self):
        subs = Subscription(self.request)
