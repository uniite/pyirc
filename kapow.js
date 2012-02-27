(function() {

  jQuery.fn.bindToObservable = function(options) {
    var element, i, item, observable, subscription, template, _len;
    element = $(this);
    observable = (options != null ? options.observable : void 0) || new ObservableList();
    template = (options != null ? options.template : void 0) || Handlebars.compile("<li>{{this}}</li>");
    console.log(observable);
    subscription = observable.subscribe("__all__", function(target, event, data) {
      var newItem;
      switch (event) {
        case "add":
          newItem = template({
            id: target,
            data: data
          });
          return $(element).append(newItem);
        case "change":
          return $(element.children()[target]).replaceWith(template({
            id: target,
            data: data
          }));
        case "remove":
          return $(element.children()[target]).remove();
      }
    });
    for (i = 0, _len = observable.length; i < _len; i++) {
      item = observable[i];
      subscription.callback(i, "add", item);
    }
    return subscription;
  };

}).call(this);
