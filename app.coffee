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

  sendMessage: =>
    index = @.conversations().indexOf @.currentConversation()
    window.client.sendMessage index, @.outgoingMessage()
    @.outgoingMessage("")

  openConversation: (conversation) =>
    index = conversation.index()
    start = (new Date).getTime();
    index = @.currentConversationIndex(index)
    console.log("TOOK " + ((new Date).getTime() - start))
    scrollNext()
    #$("body").animate scrollLeft: "+" + ($(window).width() * 2), 0



$(window).resize ->
 reformat()
 window.scrollSnap()

$(document).bind "scroll", ->
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


window.currentPane = ->
  return $("body").scrollLeft() / $(window).width()

window.scrollToPane = (pane) ->
  targetX = $(window).width() * pane
  # First, cancel any animations currently running on the body
  # (most likely previous snap animations)
  $("body").stop(true, true)
  $("body").animate scrollLeft: targetX,
    duration: 200


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

  # Do the actual snapping
  # If the distance we need to scroll is fairly small, don't bother animating.
  if Math.abs(scrollX - targetX) < 10
    $("body").scrollLeft(targetX)
  # Otherwise, do a quick animation
  else
    scrollToPane(targetX / windowWidth)

  # Refresh the page formatting
  window.reformat()




window.reformat = ->
  windowWidth = $(window).width()
  $(".footer .inner-left").width(windowWidth - $(".footer .inner-right").width())
  window.scrollSnapThreshold = windowWidth / 2
  true



$ ->
  $(window).bind "touchdown", (e) ->
    $("body").stop true, false
    return true
  $(window).bind "touchstart", (e) ->
    $("body").stop true, false
    return true
  $(window).bind "touchmove", (e) ->
    $("body").stop true, false
    return true
  window.reformat()

  window.client = new JSONRPCClient
    url: "ws://192.168.7.100:8000/",
    ready: =>
      console.log "Ready callback"
      client.getSession (result) =>
        console.log "Got Session"
        #console.log result
        window.session = new SessionModel(result)
        ko.applyBindings window.session
        $(document).scrollLeft 0
        window.reformat()

    notification: (data) =>
      #shouldScroll = $(document).scrollTop() == ($(document).height() - $(window).height())
      console.log "Notification: " + data
      Util.applyDelta session, data.delta
      #$(document).scrollTop $(document).height() - $(window).height() if shouldScroll
      #newViewModel = ko.mapping.fromJS({messages: data});
      #for message in newViewModel.messages()
      #  viewModel.messages.push message

    error: (e) => console.log "Error: " + JSON.stringify(e); throw e;
