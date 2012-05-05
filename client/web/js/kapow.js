(function() {
  var domCreate;

  domCreate = function(htmlStr) {
    var frag, temp;
    frag = document.createDocumentFragment();
    temp = document.createElement('div');
    temp.innerHTML = htmlStr;
    while (temp.firstChild) {
      frag.appendChild(temp.firstChild);
    }
    return frag;
  };

  jQuery.fn.bindToObservable = function(options) {
    var addBuffer, element, flushAddBuffer, i, item, observable, subscription, template, _len;
    element = $(this);
    observable = (options != null ? options.observable : void 0) || new ObservableList();
    template = (options != null ? options.template : void 0) || Handlebars.compile("<li>{{this}}</li>");
    console.log(observable);
    addBuffer = [];
    flushAddBuffer = function() {
      element[0].appendChild(domCreate(addBuffer.join("")));
      return addBuffer = [];
    };
    subscription = observable.subscribe("__all__", function(target, event, data, buffer) {
      switch (event) {
        case "add":
          addBuffer.push(template({
            id: target,
            data: data
          }));
          if (!buffer) return flushAddBuffer();
          break;
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
      subscription.callback(i, "add", item, true);
    }
    flushAddBuffer();
    return console.log("Flushed");
  };

}).call(this);
