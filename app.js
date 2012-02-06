(function() {
  var JSONRPCClient, Message;

  JSONRPCClient = (function() {

    function JSONRPCClient(options) {
      var _this = this;
      this.options = options;
      console.log(this.options);
      this.idCounter = 0;
      this.callbacks = {};
      this.ws = new WebSocket(this.options.url);
      this.ws.onopen = function(e) {
        console.log("Connected!");
        return _this._call("listMethods", [
          function(result) {
            return _this._updateMethods(result);
          }
        ]);
      };
      this.ws.onmessage = function(e) {
        var response;
        console.log(e.data);
        response = JSON.parse(e.data);
        if (response.notification) {
          if (_this.options && typeof _this.options.notification === "function") {
            return _this.options.notification(response.notification);
          }
        } else if (_this.callbacks[response.id]) {
          _this.callbacks[response.id](response.result);
          return delete _this.callbacks[response.id];
        }
      };
      this.ws.onerror = this.options.error;
    }

    JSONRPCClient.prototype._updateMethods = function(methods) {
      var method, _i, _len;
      for (_i = 0, _len = methods.length; _i < _len; _i++) {
        method = methods[_i];
        this[method] = (function(method) {
          return function() {
            return this._call(method, Array.prototype.slice.call(arguments));
          };
        })(method);
      }
      console.log("Ready!");
      if (this.options && typeof this.options.ready === "function") {
        return this.options.ready();
      }
    };

    JSONRPCClient.prototype._call = function(method, params) {
      if (typeof params[params.length - 1] === "function") {
        this.callbacks[this.idCounter] = params.pop();
      }
      return this.ws.send(JSON.stringify({
        id: this.idCounter++,
        method: method,
        params: params
      }));
    };

    return JSONRPCClient;

  })();

  Message = (function() {

    function Message(sender, body) {
      this.sender = sender;
      this.body = body;
      this.sender = ko.observable(this.sender);
      this.body = ko.observable(this.body);
    }

    return Message;

  })();

  $(function() {
    var AppViewModel, viewModel,
      _this = this;
    AppViewModel = (function() {

      function AppViewModel() {}

      AppViewModel.prototype.messages = ko.observableArray([new Message("someguy", "hi"), new Message("me", "hello")]);

      AppViewModel.prototype.addMessage = function() {
        return this.messages.push(new Message("someguy", "hmmm"));
      };

      return AppViewModel;

    })();
    window.client = new JSONRPCClient({
      url: "ws://127.0.0.1:8000/",
      ready: function() {
        return client.getMessages(function(result) {
          console.log("Got: " + result);
          return ko.mapping.fromJS({
            messages: result
          }, {}, viewModel);
        });
      },
      notification: function(data) {
        var message, newViewModel, _i, _len, _ref, _results;
        console.log("Notification: " + data);
        newViewModel = ko.mapping.fromJS({
          messages: data
        });
        _ref = newViewModel.messages();
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          message = _ref[_i];
          _results.push(viewModel.messages.push(message));
        }
        return _results;
      },
      error: function(e) {
        console.log("Error!");
        throw e;
      }
    });
    viewModel = new AppViewModel;
    return ko.applyBindings(viewModel);
  });

}).call(this);
