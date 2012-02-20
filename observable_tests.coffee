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
    for i in [0..2]
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

  # This is needed because emulating an array/list isn't straightforward in JavaScript
  test "list array emulation", ->
    # Create an observable list with a few items in it
    observableList = new ObservableList("hello", "on", "this", "fine", "day")
    # Check the internal array
    deepEqual observableList.list, ["hello", "on", "this", "fine", "day"]
    # Check the length getter
    equal observableList.length, 5
    # Check the item getters
    for i in [0..5]
      equal observableList[i], observableList.list[i]
    # Remove an item and check again
    equal observableList.remove("on"), "on"
    equal observableList.length, 4
    for i in [0..4]
      equal observableList[i], observableList.list[i]
    # Add a few items and check once more
    equal observableList.push("..."), "..."
    equal observableList.push("hello"), "hello"
    equal observableList.push("there"), "there"
    deepEqual observableList.list, ["hello", "this", "fine", "day", "...", "hello", "there"]
    equal observableList.length, 7
    for i in [0..6]
      equal observableList[i], observableList.list[i]
    # Splice some things
    observableList.splice 2, 4
    deepEqual observableList.list, ["hello", "this", "there"]
    observableList.splice 2, 0, "aa", "ab", "bc"
    deepEqual observableList.list, ["hello", "this", "aa", "ab", "bc", "there"]


  test "list add", ->
    # Create an observable list
    observable_list = new ObservableList()
    # Subscribe to add events
    subscription = observable_list.subscribe("add", callback)
    # Add an item to it
    observable_list.push("nom")
    # Ensure this triggered the callback
    deepEqual callbackResult, [0, "nom"]

  test "list remove", ->
    # Create an observable dict
    observable_list = new ObservableList("one", "of", "these", "things")
    # Subscribe to remove events
    subscription = observable_list.subscribe("remove", callback)
    # Remove an item from it
    observable_list.remove("these")
    # Ensure this triggered the callback
    deepEqual callbackResult, [2, "these"]

  test "list change", ->
    # Create an observable dict
    observable_list = new ObservableList("something", "might", "change")
    # Subscribe to change events
    subscription = observable_list.subscribe("change", callback)
    # Change an item in it
    observable_list[1] = "will"
    # Ensure this triggered the callback
    deepEqual callbackResult, [1, "will"]

  test "list propagation", ->
    # Create an observable list that contains other observables
    observable_list = new ObservableList(new Alerter(), new Alerter())
    # Subscribe to all events
    subscription = observable_list.subscribe("__all__", callback)
    # Trigger an alert on something in the list
    observable_list.list[1].alert()
    # Ensure this triggered the callback
    deepEqual callbackResult, [[1, null], "alert", "Alert!"]

  test "list double propagation", ->
    class MiddleMan extends SimpleObservable
      constructor: ->
        @children = new ObservableList()
    # Create an observable list in an observable in an onbservable list
    middle_man = new MiddleMan()
    parent = new ObservableList()
    # Subscribe to the to-level list
    parent.subscribe("__all__", callback)
    # Add something to it
    parent.push(middle_man)
    # Ensure this tells us the item was added at index 0 of the top-level
    deepEqual callbackResult, [0, "add", middle_man]
    callbackResult = null
    # Add a few things to the inner list
    middle_man.children.push("hi!")
    middle_man.children.push("hello!")
    # Ensure we get told the string was added at parent[0].children[0]
    deepEqual callbackResult,  [[0, "children", 1], "add", "hello!"]

  test "list toString", ->
    deepEqual (new ObservableList(1, 2, 3)).toString(), [1, 2, 3].toString()

  test "list toDict", ->
    deepEqual new ObservableList(1, 2, 3).toDict(), [1, 2, 3]
