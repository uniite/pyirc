import collections
from simple_observable import SimpleObservable

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
        if not self._subscriptions:
            for i in range(len(self.list)):
                item = self.list[i]
                if issubclass(item.__class__, SimpleObservable):
                    # Make sure it is prefixed with the list index
                    self._subscriptions.append(item.subscribe("__all__", self._notify, prefix=i))
            # Proceed on with the normal subscription process
        SimpleObservable.subscribe(self, event, callback, shared, prefix)
