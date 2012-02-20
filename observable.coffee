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
        if v?.isObservable?()
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

  addSubscription: (observable, event, prefix) ->
    event or= "__all__"
    @_subscriptions or= []
    if observable?.isObservable?()
      ourCallback = (t, e, d) => @_notify(t, e, d)
      @_subscriptions.push(observable.subscribe(event, ourCallback, undefined, prefix))

  removeSubscriptions: (observable, cancel) ->
    if observable?.isObservable?()
      for subscription in [s for s in @_subscriptions when s.observable == observable]
        if cancel
          subscription.cancel()
        @_subscriptions.remove(subscription)



class ObservableList extends SimpleObservable
  constructor: ->
    @list = []
    @__defineGetter__ "length", => @list.length

    for v in arguments
      @_insert @length, v

  __getitem__: (i) -> @list[i]


  _remove: (i) ->
    v = @list[i]
    # Notify our subscribers of the removal
    @_notify i, "remove", v
    # Unsubscribe from the item if it is observable
    @removeSubscriptions v
    # Go ahead with the normal removal operation
    @list.splice i, 1
    # Delete the last getter/setter, in terms of numeric order,
    # since it will no longer be needed
    delete @[@length]
    # Return the removed item
    v


  remove: (item_to_remove) ->
    for v, i in @list
      if v == item_to_remove
        return @_remove i

  _setitem__: (i, v) ->
    # Notify our subscribers of the change
    @_notify(i, "change", v)
    # If we're replacing an observable, remove any subscriptions to it
    @removeSubscriptions(@list[i])
    # Subscribe to the new item if it is observable
    @addSubscription(v, i)
    # Go ahead with the normal setitem operation
    @list[i] = v

  _insert: (i, v) =>
    # Notify our subscribers of the addition
    @_notify(i, "add", v)
    # Subscribe to the new item if it is observable
    @addSubscription(v, undefined, i)
    # Go ahead with the normal insert operation
    @list.splice(i, 0, v)
    # Define a getter and setter for this item, to emulate an array
    @__defineGetter__ i, => @list[i]
    @__defineSetter__ i, (value) => @_setitem__ i, value
    # Return the added value
    v

  push: (v) => @_insert(@list.length, v)

  splice: (i, n) ->
    # TODO: support negative values for i
    # A remove operation
    if n > 0
      # Remove n items starting at the specified index
      for x in [0...n]
        @_remove i
    # An add operation
    else
      # Insert the given items at the specified index
      for j in [2...arguments.length]
        console.log @list.join(", ")
        @_insert i + j - 2, arguments[j]
      console.log @list.join(", ")

  toString: ->
    @list.toString()

  toDict: ->
    @list

  subscribe: (event, callback, shared, prefix) =>
    # Create a subscriptions list if we don't already have one
    @_subscriptions or= []
    # If this is our first or only subscription,
    # look for list items from which we can propagate events
    if @_subscriptions.length is 0
      for i in [0...@list.length]
        item = @list[i]
        if item?.isObservable?()
          # Make sure it is prefixed with the list index
          ourCallback = (t, e, d) => @_notify(t, e, d)
          @_subscriptions.push(item.subscribe("__all__", ourCallback, true, i))
    # Proceed on with the normal subscription process
    super(event, callback, shared, prefix)



window.SimpleObservable = SimpleObservable
window.ObservableList = ObservableList

