from subscription import Subscription




class SimpleObservable(object):


    def _notify(self, target, event, data):
        """ Notify all subscribers of an event, """

        # Don't do anything if we don't have any subscribers
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
        """
        Subscribe to this Observable.

        Args:
            event (str): The event to subscribe to ("add", "change", or "remove").
            callback (func): A callback for when the event occurs.
                             Should accept (target, data) if shared=False, or (target, devent, data) if shared=True.

        Kwargs:
            shared (bool): If True, indicates callback is a shared callback.
            prefix (list): A prefix to apply to the target when calling the callback.


        Returns a Subscription.
        """

        # If this is our first or only subscriber,
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
            # Return the subscription
        return s


    def unsubscribe(self, subscription):
        """ Unsubscribe from this Observable (see Subscription.cancel) """

        # Remove the given subscription from our subscribers list.
        self._subscribers[subscription.event].remove(subscription)
        # Clean up _subscribers if nobody is subscribed to this event anymore
        if self._subscribers[subscription.event] == []:
            del self._subscribers[subscription.event]
        # If we not longer have any subscribers,
        # Unsubscribe from all our children to help with garbage collection
        if self._subscribers == {}:
            for s in self._subscriptions:
                s.cancel()
            self._subscriptions = []


    def add_subscription(self, observable, event="__all__", prefix=None):
        """ Subscribe to a child Observable (for internal use) """

        if not hasattr(self, "_subscriptions"):
            self._subscriptions = []
        if issubclass(observable.__class__, SimpleObservable):
            self._subscriptions.append(observable.subscribe(event, self._notify, prefix=prefix))


    def remove_subscriptions(self, observable, cancel=True):
        """ Unsubscribe to a child Observable (for internal use) """

        if issubclass(observable.__class__, self.__class__):
            for subscription in [s for s in self._subscriptions if s.observable == observable]:
                if cancel:
                    subscription.cancel()
                self._subscriptions.remove(subscription)
