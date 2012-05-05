domCreate = (htmlStr) ->
  frag = document.createDocumentFragment()
  temp = document.createElement('div')
  temp.innerHTML = htmlStr
  while (temp.firstChild)
    frag.appendChild(temp.firstChild)
  frag

jQuery.fn.bindToObservable = (options) ->
  element = $(this)
  observable = options?.observable or new ObservableList()
  template = options?.template or Handlebars.compile("<li>{{this}}</li>")
  console.log observable
  addBuffer = [];

  flushAddBuffer = () ->
    element[0].appendChild(domCreate(addBuffer.join("")))
    addBuffer = []

  subscription = observable.subscribe "__all__", (target, event, data, buffer) ->
    switch event
      when "add"
        addBuffer.push template(id: target, data: data)
        flushAddBuffer() unless buffer
      when "change"
        $(element.children()[target]).replaceWith template(id: target, data: data)
      when "remove"
        $(element.children()[target]).remove()

  for item, i in observable
    subscription.callback i, "add", item, true
  flushAddBuffer()
  console.log("Flushed")
