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
    def _notify(self, target, event, data):
        if not hasattr(self, "_subscribers"):
            return
        for s in self._subscribers.get(event, []) + self._subscribers.get("__all__", []):
            if s.shared:
                if s.prefix != None:
                    if type(target) != tuple:
                        target = (target,)
                    s.callback((s.prefix,) + target, event, data)
                else:
                    s.callback(target, event, data)
            else:
                s.callback(target, data)

    def subscribe(self, event, callback, shared=False, prefix=None):
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

    def add_subscription(self, observable, event="__all__", prefix=None):
        if not hasattr(self, "_subscriptions"):
            self._subscriptions = []
        if issubclass(observable.__class__, SimpleObservable):
            self._subscriptions.append(observable.subscribe(event, self._notify, prefix=prefix))

    def remove_subscriptions(self, observable, cancel=True):
        if issubclass(observable.__class__, self.__class__):
            for subscription in [s for s in self._subscriptions if s.observable == observable]:
                if cancel:
                    subscription.cancel()
                self._subscriptions.remove(subscription)




class ObservableList(collections.MutableSequence, SimpleObservable):

    def __init__(self, *args):
        self.list = list()
        self.extend(list(args))

    def __len__(self): return len(self.list)

    def __getitem__(self, i): return self.list[i]

    def __delitem__(self, i):
        # Notify our subscribers of the removal
        v = self.list[i]
        self._notify(i, "remove", v)
        # Unsubscribe from the item if it is observable
        self.remove_subscriptions(v)
        # Go ahead with the normal insert operation
        del self.list[i]

    def __setitem__(self, i, v):
        # Notify our subscribers of the change
        self._notify(i, "change", v)
        # If we're replacing an observable, remove any subscriptions to it
        self.remove_subscriptions(self.list[i])
        # Subscribe to the new item if it is observable
        self.add_subscription(v, prefix=i)
        # Go ahead with the normal setitem operation
        self.list[i] = v

    def insert(self, i, v):
        # Notify our subscribers of the addition
        self._notify(i, "add", v)
        # Subscribe to the new item if it is observable
        self.add_subscription(v, prefix=i)
        # Go ahead with the normal insert operation
        self.list.insert(i, v)

    def __str__(self):
        return str(self.list)

    def to_dict(self):
        return self.list

    def subscribe(self, event, callback, shared=False, prefix=None):
        # Create a subscriptions list if we don't already have one
        if not hasattr(self, "_subscriptions"):
            self._subscriptions = []
        # If this is our first or only subscription,
        # look for list items from which we can propagate events
        if not hasattr(self, "_subscriptions") or self._subscriptions == []:
            for i in range(len(self.list)):
                item = self.list[i]
                if issubclass(item.__class__, SimpleObservable):
                    # Make sure it is prefixed with the list index
                    self._subscriptions.append(item.subscribe("__all__", self._notify, prefix=i))
        # Proceed on with the normal subscription process
        SimpleObservable.subscribe(self, event, callback, shared, prefix)



class ObservableDict(dict, SimpleObservable):
    def __delitem__(self, k):
        # Notify our subscribers of the removal
        self._notify(k, "remove", self[k])
        # Unsubscribe from the item if it is observable
        self.remove_subscriptions(self[k])
        # Proceed with the normal dict item deletion
        dict.__delitem__(self, k)

    def __setitem__(self, k, v):
        # If already have this key, we're changing an item
        if self.has_key(k):
            # Notify out subscribers of the change
            self._notify(k, "change", v)
            # Unsubscribe from the old item if it is observable
            self.remove_subscriptions(self[k])
        # A new item is being added
        else:
            # Notify out subscribers of the addition
            self._notify(k, "set", v)
            # Subscribe to the new item if it is observable
            self.add_subscription(v, prefix=k)
        # Proceed with the normal dict item set
        dict.__setitem__(self, k, v)

    def subscribe(self, event, callback, shared=False, prefix=None):
        # Create a subscriptions list if we don't already have one
        if not hasattr(self, "_subscriptions"):
            self._subscriptions = []
        # If this is our first or only subscription,
        # look for list items from which we can propagate events
        if not hasattr(self, "_subscriptions") or self._subscriptions == []:
            for k,v in self.iteritems():
                if issubclass(v.__class__, SimpleObservable):
                    # Make sure it is prefixed with the list index
                    self._subscriptions.append(v.subscribe("__all__", self._notify, prefix=str(k)))
        # Proceed on with the normal subscription process
        SimpleObservable.subscribe(self, event, callback, shared, prefix)

