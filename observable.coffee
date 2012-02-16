class Subscription
  constructor: (@callback, @observable, @event, @shared, @prefix) ->

  cancel: ->
    @observable.unsubscribe(@)


class SimpleObservable
  isObservable: ->
    true

  _notify: (target, event, data) ->
    return unless @_subscribers?
    @_subscribers[event] or= []
    @_subscribers["__all__"] or= []
    for s in $.extend(@_subscribers[event] or [], @_subscribers["__all__"] or [])
      if s.shared
        if s.prefix?
          if not target?.push
            target = [target]
          new_target = $.merge([s.prefix], target)
          s.callback(new_target, event, data)
        else
          s.callback(target, event, data)
      else
        s.callback(target, data)

  subscribe: (event, callback, shared, prefix) ->
    # If this is our first or only subscriber,
    # look for children from which we can propagate events
    if not @_subscriptions?
      @_subscriptions = []
      for k,v of @
        # If the given attribute is an observable "child", subscribe to it
        if v.isObservable?()
          # Make sure it is prefixed with the attribute name
          ourCallback = (t, e, d) => @_notify(t, e, d)
          @_subscriptions.push(v.subscribe("__all__", ourCallback, true, k))
    # Create the subscription
    s = new Subscription(callback, @, event, (shared or event == "__all__"), prefix)
    # Subscribe it to the specified event
    @_subscribers or= {}
    @_subscribers[event] or= []
    @_subscribers[event].push(s)
    # Return the subscription
    s

  unsubscribe: (subscription) ->
    # Removed the given subscription from our subscribers list
    subscribers = @_subscribers[subscription.event]
    subscribers.splice(subscribers.indexOf(subscription), 1)
    # Clean up _subscribers if nobody is subscribed to this event anymore
    if @_subscribers[subscription.event].length == 0
      delete @_subscribers[subscription.event]
    # If we not longer have any subscribers,
    # unsubscribe from all our children to help with garbage collection
    if $.isEmptyObject @_subscribers
      for s in @_subscriptions
        s.cancel()
      @_subscriptions = []

  add_subscription: (observable, event, prefix) ->
    event or= "__all__"
    @_subscriptions or= []
    if observable.isObservable?()
      @_subscriptions.push(observable.subscribe(event, @_notify, undefined, prefix))

  remove_subscriptions: (observable, cancel) ->
    if observable.isObservable?()
      for subscription in [s for s in @_subscriptions when s.observable == observable]
        if cancel
          subscription.cancel()
        @_subscriptions.remove(subscription)



window.SimpleObservable = SimpleObservable

