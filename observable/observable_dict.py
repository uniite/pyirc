from simple_observable import SimpleObservable

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
