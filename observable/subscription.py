class Subscription(object):
    def __init__(self, callback, observable=None, event=None, shared=False, prefix=None):
        self.callback = callback
        self.observable = observable
        self.event = event
        self.shared = shared
        self.prefix = prefix

    def cancel(self):
        self.observable.unsubscribe(self)
