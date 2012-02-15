$ ->
  class Alerter extends SimpleObservable
    alert: ->
      @._notify(null, "alert", "Alert!")
    warn: ->
      @._notify(null, "warn", "Warning!")

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
    expect 8
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