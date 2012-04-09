if not window.WebSocket? and window.MozWebSocket?
  window.WebSocket = window.MozWebSocket

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
      #console.log("RESPONSE " + e.data)
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

    @ws.onclose = @options.error
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


class Util
  @applyDelta: (target, delta) ->
    # Figure out what the target of the delta is,
    # which will be based off of target
    last_key = delta.target.pop()
    for key in delta.target
      target = target[key]
      last_target = target
      if typeof target == "function"
        target = target()
    # Apply the delta to the target based on the event type
    data = delta.data
    switch delta.event
      when "add"
        last_target.push(data)
      when "change", "set"
        last_target[last_key] = data
      when "remove"
        last_target._remove(last_key)



class SessionModel
  constructor: (data) ->
    @conversations = data.conversations
    for c in @conversations
      c.messages = new ObservableList(c.messages)
      c.users = new ObservableList(c.users)
    @conversations = new ObservableList(@conversations)

  sendMessage: =>
    index = @.conversations().indexOf @.currentConversation()
    window.client.sendMessage index, @.outgoingMessage()
    @.outgoingMessage("")

  openConversation: (conversation) =>
    index = conversation.index()
    start = (new Date).getTime();
    index = @.currentConversationIndex(index)
    console.log("TOOK " + ((new Date).getTime() - start))
    autoScrollMessages()
    scrollNext()
    #$("body").animate scrollLeft: "+" + ($(window).width() * 2), 0



$(window).resize ->
 reformat()


window.messagesScrolledToBottom = ->
  scrollContainer = $("#ConversationInner")
  scrollTarget = $("#MessagesList")
  scrollContainer.scrollTop() == (scrollTarget.height() - scrollContainer.height())

window.autoScrollMessages = ->
  scrollContainer = $("#ConversationInner")
  scrollTarget = $("#MessagesList")
  scrollContainer.scrollTop scrollTarget.height() - scrollContainer.height()



window.reformat = ->
  windowWidth = $(window).width()
  $(".footer .inner-left").width(windowWidth - $(".footer .inner-right").width())
  autoScrollMessages()
  true



$ ->
  window.reformat()

  window.client = new JSONRPCClient
    url: "ws://192.168.7.100:8000/",
    #url: "ws://shoebox.jbotelho.com:42450/",
    ready: =>
      console.log "Ready callback"
      rpcStart = (new Date).getTime()
      client.getSession (result) =>
        rpcEnd = ((new Date).getTime() - rpcStart)
        $("#JSONTime").text("Global: " + rpcEnd + "ms")
        console.log "Got Session"
        #console.log result
        start = (new Date).getTime()
        window.session = new SessionModel(result)
        $("#UsersListInner").hide()
        $("#UsersListInner").bindToObservable
          observable: session.conversations[1].messages
          template: Handlebars.compile($("#MessageItem").html())
        console.log("PROCESS " + ((new Date).getTime() - start))
        #$(document).scrollLeft 0
        #window.reformat()
        window.setTimeout () ->
          $("#UsersListInner").show()
          end = ((new Date).getTime() - start)
          $("#RenderTime").text("Render: " + end + "ms")
        , 0

    notification: (data) =>
      console.log "Notification: " + data
      shouldScroll = messagesScrolledToBottom()
      Util.applyDelta session, data.delta
      autoScrollMessages() if shouldScroll
      #newViewModel = ko.mapping.fromJS({messages: data});
      #for message in newViewModel.messages()
      #  viewModel.messages.push message

    error: (e) => console.log "Error: " + JSON.stringify(e); throw e;
