$ ->
  class Alerter extends SimpleObservable
    alert: ->
      @_notify(null, "alert", "Alert!")
    warn: ->
      @_notify(null, "warn", "Warning!")

  callbackResult = null
  QUnit.testStart ->
    callbackResult = null

  callback = (t, e, d) ->
    if d?
      callbackResult = [t, e, d]
    else
      callbackResult = [t, e]

  multiCallback = (t, e, d) ->
    callbackResult or= []
    if d?
      callbackResult.push([t, e, d])
    else
      callbackResult.push([t, e])

  test "subscribe", ->
    # Create an observable
    alerter = new Alerter()
    # Subscribe to its alert event
    subscription = alerter.subscribe("alert", callback)
    # Make sure the subscription is there
    for k,v of subscription
      equal alerter._subscribers["alert"][0][k], v
    # Trigger an event
    alerter.alert()
    # Make sure it called the callback
    equal callbackResult.length, 2
    equal callbackResult[1], "Alert!"
    undefined

  test "susbcribe multiple", ->
    # Create an observable
    alerter = new Alerter()
    # Subscribe to its alert event thrice
    for i in [1..3]
      alerter.subscribe("alert", multiCallback)
    # Trigger an event
    alerter.alert()
    # Make sure it called the callback thrice
    equal callbackResult.length, 3
    for i in [0..2]
      deepEqual callbackResult[i], [null, "Alert!"]

  test "subscribe all", ->
    # Create an observable
    alerter = new Alerter()
    # Subscribe to everything
    subscription = alerter.subscribe("__all__", callback)
    # Trigger an event
    alerter.alert()
    # Make sure it called the callback
    deepEqual callbackResult, [null, "alert", "Alert!"]
    # Trigger another event
    alerter.warn()
    # Make sure it called the callback
    deepEqual callbackResult, [null, "warn", "Warning!"]

  test "unsubscribe", ->
    # Create an observable
    alerter = new Alerter()
    # Subscribe to its alert event
    subscription = alerter.subscribe("alert", callback)
    # Unsubscribe via the observable
    alerter.unsubscribe(subscription)
    # Trigger an event
    alerter.alert()
    # Make sure it didn't call the callback
    equal callbackResult, null

  test "subscription cancel", ->
    # Create an observable
    alerter = new Alerter()
    # Subscribe to its alert event
    subscription = alerter.subscribe("alert", callback)
    # Unsubscribe via the subscription
    subscription.cancel()
    # Trigger an event
    alerter.alert()
    # Make sure it did not call the callback
    equal callbackResult, null

  test "propagation", ->
    # Create an observable that contains an observable
    class SuperAlerter extends SimpleObservable
      constructor: (@alerter, @alerter2) ->
    super_alerter = new SuperAlerter(new Alerter(), new Alerter())
    # Subscribe to everything
    subscription = super_alerter.subscribe("__all__", callback)
    # Trigger an event on the second Alerter
    super_alerter.alerter2.alert()
    # Make sure it propagated via super_alerter, with the right prefix
    deepEqual callbackResult, [["alerter2", null], "alert", "Alert!"]

  test "garbage collection", ->
    status = {"deleted": false}
    class ParanoidAlerter extends SimpleObservable
      # Doesn't actually work in JS :(
      __del__: ->
        @status["deleted"] = true
    paranoid_alerter = new ParanoidAlerter()
    paranoid_alerter.status = status
    # Give it a child observable to subscribe to
    paranoid_alerter.child = new Alerter()
    # Give it a subscription
    subscription = paranoid_alerter.subscribe("__all__", callback)
    # Make sure it sticks
    deepEqual paranoid_alerter._subscribers["__all__"], [subscription]
    notDeepEqual paranoid_alerter.child._subscribers["__all__"], []
    # Cancel and delete the subscription to remove all references to it
    subscription.cancel()
    delete subscription
    # Ensure the subscriptions are all cleaned up
    deepEqual paranoid_alerter._subscribers, {}
    deepEqual paranoid_alerter._subscriptions, []
    deepEqual paranoid_alerter.child._subscribers, {}
    # Ensure paranoid_alerter can now be garbage collected
    delete paranoid_alerter
    # Doesn't apply to JS
    #ok status["deleted"]
