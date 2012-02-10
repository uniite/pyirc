class JSONRPCClient
  constructor: (@options) ->
    console.log @options
    # Used as the id for JSON-RPC calls (incremented every call)
    @idCounter = 0
    # Keeps track of which request IDs map to which callbacks
    @callbacks = {}

    # Connect to the given WebSocket URL
    @ws = new WebSocket @options.url
    # When the connection is ready,
    # immediately get a list of available JSON-RPC methods
    @ws.onopen = (e) =>
      console.log "Connected!"
      @_call "listMethods", [(result) => @_updateMethods(result)]

    # When we get a WebSocket message...
    @ws.onmessage = (e) =>
      console.log e.data
      # Parse the response
      response = JSON.parse(e.data)

      # If the response is a notificatiion from the server...
      if response.notification
        # Hand it off the notification handler
        if @options && typeof @options.notification == "function"
          @options.notification(response.notification)
      # If this response has a callback, call it
      else if @callbacks[response.id]
        @callbacks[response.id](response.result)
        delete @callbacks[response.id]

    @ws.onerror = @options.error

  _updateMethods: (methods) ->
    # Setup wrapper methods for each of the JSON-RPC methods,
    # so you can call myClient.someMethod("args")
    for method in methods
      # Need to bind the wrapper to the current value of method
      @[method] = do (method) ->
          # The wrapper for _call
          -> @_call method, Array.prototype.slice.call(arguments)

    console.log "Ready!"
    # Call the ready callback, if given
    if @options && typeof @options.ready == "function"
      @options.ready()

  _call: (method, params) ->
    # Register a callback for this request, if we're given one
    if typeof params[params.length - 1] == "function"
      @callbacks[@idCounter] = params.pop()

    # Send a JSON-encoded RPC call,
    # Note the id increment, so each request has a unique id
    @ws.send JSON.stringify
       id: @idCounter++
       method: method
       params: params



class Message
  constructor: (@sender, @body) ->
    @sender = ko.observable(@sender)
    @body = ko.observable(@body)


class Util
  @applyDelta: (target, delta) ->
    console.log(delta)
    # Figure out what the target of the delta is,
    # which will be based off of target
    last_key = delta.target.pop()
    for key in delta.target
      target = target[key]
      last_target = target
      if typeof target == "function"
        target = target()
    # Apply the delta to the target based on the event type
    data = ko.mapping.fromJS delta.data
    switch delta.event
      when "add"
        last_target.push(data)
      when "change", "set"
        last_target.replace(last_key, data)
      when "remove"
        last_target.remove(last_key)




class ConversationModel
  name: ko.observable()
  messages: ko.observableArray([new Message("someguy", "hi"), new Message("me", "hello")])
  addMessage: ->
    @messages.push(new Message("someguy", "hmmm"))

class SessionModel
  name: ko.observable()

$ ->
  window.client = new JSONRPCClient
    url: "ws://127.0.0.1:8000/",
    ready: =>
      client.getSession (result) =>
        console.log "Got: "
        console.log result
        window.session = ko.mapping.fromJS(result);
        ko.applyBindings session
    notification: (data) =>
      shouldScroll = $(document).scrollTop() == ($(document).height() - $(window).height())
      console.log "Notification: " + data
      Util.applyDelta session, data.delta
      $(document).scrollTop $(document).height() - $(window).height() if shouldScroll
      #newViewModel = ko.mapping.fromJS({messages: data});
      #for message in newViewModel.messages()
      #  viewModel.messages.push message

    error: (e) => console.log "Error!"; throw e;
