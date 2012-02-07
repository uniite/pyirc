import collections



class Subscription(object):
    def __init__(self, callback, observable=None, event=None, shared=False, prefix=None):
        self.callback = callback
        self.observable = observable
        self.event = event
        self.shared = shared
        self.prefix = prefix

    def cancel(self):
        self.observable.unsubscribe(self)


class SimpleObservable(object):
    def _notify(self, event, *args, **kwargs):
        for s in self._subscribers.get(event, []) + self._subscribers.get("__all__", []):
            if s.shared:
                if s.prefix:
                    s.callback(".".join((s.prefix, event)), *args, **kwargs)
                else:
                    s.callback(event, *args, **kwargs)
            else:
                s.callback(*args, **kwargs)

    def subscribe(self, event, callback, shared=False, prefix=""):
        # If this is our first or only subscription,
        # look for children from which we can propagate events
        if not hasattr(self, "_subscriptions") or self._subscriptions == []:
            self._subscriptions = []
            for k,v in vars(self).iteritems():
                # If the given attribute is an observable "child", subscribe to it
                if issubclass(v.__class__, SimpleObservable):
                    # Make sure it is prefixed with the attribute name
                    self._subscriptions.append(v.subscribe("__all__", self._notify, prefix=k))
        # Create the subscription
        s = Subscription(callback, observable=self, event=event, shared=(shared or event == "__all__"), prefix=prefix)
        # Subscribe it to the specified event
        if not hasattr(self, "_subscribers"):
            self._subscribers = {}
        if self._subscribers.has_key(event):
            self._subscribers[event].append(s)
        else:
            self._subscribers[event] = [s]
        # Return teh subscription
        return s

    def unsubscribe(self, subscription):
        # Removed the given subscription from our subscribers list
        self._subscribers[subscription.event].remove(subscription)
        # Clean up _subscribers if nobody is subscribed to this event anymore
        if self._subscribers[subscription.event] == []:
            del self._subscribers[subscription.event]
        # If we not longer have any subscribers,
        # unsubscribe from all our children to help with garbage collection
        if self._subscribers == {}:
            for s in self._subscriptions:
                s.cancel()
            self._subscriptions = []




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

    def subscribe(self, event, callback, shared=False, prefix=""):
        # If this is our first or only subscription,
        # look for list items from which we can propagate events
        if not hasattr(self, "_subscriptions") or self._subscriptions == []:
            for i in range(len(self.list)):
                item = self.list(i)
                if issubclass(item.__class__, SimpleObservable):
                    # Make sure it is prefixed with the list index
                    self._subscriptions.append(item.subscribe("__all__", self._notify, prefix=("[%s]" % i)))
        # Proceed on with the normal subscription process
        SimpleObservable.subscribe(self, event, callback, shared, prefix)

