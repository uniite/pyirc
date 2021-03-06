class JSONRPCClient
  constructor: (@options) ->
    console.log @options
    # Used as the id for JSON-RPC calls (incremented every call)
    @idCounter = 0
    # Keeps track of which request IDs map to which callbacks
    @callbacks = {}

    # Connect to the given WebSocket URL
    window.WebSocket ||= MozWebSocket
    @ws = new WebSocket @options.url
    # When the connection is ready,
    # immediately get a list of available JSON-RPC methods
    @ws.onopen = (e) =>
      console.log "Connected!"
      @_call "listMethods", [(result) => @_updateMethods(result)]

    # When we get a WebSocket message...
    @ws.onmessage = (e) =>
      console.log("RESPONSE " + e.data)
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



class Message
  constructor: (@sender, @body) ->
    @sender = ko.observable(@sender)
    @body = ko.observable(@body)


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
    # If the delta isn't guarunteed to contain constant/static data,
    # make the data observable.
    # TODO: See if it is worth it, resource-wise.
    # You could do cool things like dynamically change username aliases
    console.log(last_key)
    if delta.constant
      data = delta.data
    else
      data = ko.mapping.fromJS delta.data
    # Apply the delta to the target based on the event type
    switch delta.event
      when "add"
        last_target.push(data)
      when "change", "set"
        last_target.replace(last_key, data)
      when "remove"
        last_target.remove(last_key)



class SessionModel
  constructor: (data) ->
    ko.mapping.fromJS(data, {}, @)
    @.currentConversationIndex = ko.observable(0)
    @.outgoingMessage = ko.observable("")
    @.currentConversation = ko.computed =>
      @.conversations()[@.currentConversationIndex()]
    @.currentMessages = ko.computed =>
      msgs = @.currentConversation().messages()
      if msgs.length > 100
        msgs.slice(msgs.length - 100, msgs.length)
      else
        msgs
    @.currentUsers = ko.computed =>
      users = @.currentConversation().users()
      if users.length > 100
        users.slice(users.length - 100, users.length)
      else
        users

  sendMessage: =>
    index = @.conversations().indexOf @.currentConversation()
    window.client.sendMessage @currentConversation().id(), @outgoingMessage()
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
 window.scrollSnap()

$(document).bind "scroll", (e) ->
  if window.scrollDone == true
    window.scrollDone = false
    return
  if window.scrollStopTimeout
    clearTimeout(window.scrollStopTimeout)
  window.scrollStopTimeout = setTimeout(window.scrollSnap, 100)
  return true

window.scrollSnapEnabled = true
window.scrollNext = ->
  scrollToPane(currentPane() + 1)

window.lastPane = 0
window.currentPane = ->
  return $("body").scrollLeft() / $(window).width()

window.scrollToPane = (pane) ->
  targetX = $(window).width() * pane
  # First, cancel any animations currently running on the body
  # (most likely previous snap animations)
  $("body").stop(true, true)
  $("body").animate scrollLeft: targetX, 200


window.messagesScrolledToBottom = ->
  scrollContainer = $("#ConversationInner")
  scrollTarget = $("#MessagesList")
  scrollContainer.scrollTop() == (scrollTarget.height() - scrollContainer.height())

window.autoScrollMessages = ->
  scrollContainer = $("#ConversationInner")
  scrollTarget = $("#MessagesList")
  scrollContainer.scrollTop scrollTarget.height() - scrollContainer.height()


window.scrollSnap = ->
  return unless window.scrollSnapEnabled
  console.warn "Snap!"

  # Figure the X coordinates of the nearest panes to the left and right
  windowWidth = $(window).width()
  scrollX = $(window).scrollLeft()
  leftPaneX = Math.floor(scrollX / windowWidth) * windowWidth
  rightPaneX = leftPaneX + windowWidth
  # Figure out pane we're closer to
  closerToLeft = ((scrollX - leftPaneX) - (windowWidth / 2)) < 0

  # Get the X coordinate of the pane we need to snap to
  if closerToLeft
    targetX = leftPaneX
  else
    targetX = rightPaneX

  # Don't do anything if we're already there
  return if scrollX == targetX

  # Do the actual snapping
  # If the distance we need to scroll is fairly small, don't bother animating.
  if Math.abs(scrollX - targetX) < 10
    $("body").scrollLeft(targetX)
  # Otherwise, do a quick animation
  else
    scrollToPane(targetX / windowWidth)

  # Refresh the page formatting
  window.reformat()


window.dragSnap = ->
  return unless window.scrollSnapEnabled
  console.warn "Snap!"

  # Figure the X coordinates of the nearest panes to the left and right
  windowWidth = $(window).width()
  scrollX = $("#PageContainer").position().left
  leftPaneX = Math.floor(scrollX / windowWidth) * windowWidth
  rightPaneX = leftPaneX + windowWidth
  # Figure out pane we're closer to
  closerToLeft = ((scrollX - leftPaneX) - (windowWidth / 2)) < 0

  # Get the X coordinate of the pane we need to snap to
  if closerToLeft
    targetX = leftPaneX
  else
    targetX = rightPaneX

  # Do the actual snapping
  # If the distance we need to scroll is fairly small, don't bother animating.
  if Math.abs(scrollX - targetX) < 10
    $("#PageContainer").css("left", targetX)
    # Otherwise, do a quick animation
  else
    $("#PageContainer").stop(true, true)
    $("#PageContainer").animate left: targetX,
      duration: 200

  # Refresh the page formatting
  window.reformat()



window.reformat = ->
  windowWidth = $(window).width()
  $(".footer .inner-left").width(windowWidth - $(".footer .inner-right").width())
  window.scrollSnapThreshold = windowWidth / 2
  autoScrollMessages()
  scrollSnap()
  true



$ ->
  window.reformat()

  w = $(window).width()

  window.client = new JSONRPCClient
    url: "ws://192.168.7.100:8000/",
    #url: "ws://shoebox.jbotelho.com:42450/",
    ready: =>
      console.log "Ready callback"
      client.getSession (result) =>
        console.log "Got Session"
        #console.log result
        window.session = new SessionModel(result)
        start = (new Date).getTime()
        ko.applyBindings window.session
        console.log(((new Date).getTime() - start) + "ms")
        $(document).scrollLeft 0
        window.reformat()

    notification: (data) =>
      console.log "Notification: " + data
      shouldScroll = messagesScrolledToBottom()
      Util.applyDelta session, data.delta
      autoScrollMessages() if shouldScroll
      #newViewModel = ko.mapping.fromJS({messages: data});
      #for message in newViewModel.messages()
      #  viewModel.messages.push message

    error: (e) => console.log "Error: " + JSON.stringify(e); throw e;
