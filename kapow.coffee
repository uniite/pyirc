jQuery.fn.bindToObservable = (options) ->
  element = $(this)
  observable = options?.observable or new ObservableList()
  template = options?.template or Handlebars.compile("<li>{{this}}</li>")
  console.log observable

  subscription = observable.subscribe "__all__", (target, event, data) ->
    switch event
      when "add"
        newItem = template(id: target, data: data)
        $(element).append newItem
      when "change"
        $(element.children()[target]).replaceWith template(id: target, data: data)
      when "remove"
        $(element.children()[target]).remove()

  for item, i in observable
    subscription.callback i, "add", item

  subscription
