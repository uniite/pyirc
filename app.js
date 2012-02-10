(function() {
  var ConversationModel, JSONRPCClient, Message, SessionModel, Util;

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

  Util = (function() {

    function Util() {}

    Util.applyDelta = function(target, delta) {
      var data, key, last_key, last_target, _i, _len, _ref;
      console.log(delta);
      last_key = delta.target.pop();
      _ref = delta.target;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        key = _ref[_i];
        target = target[key];
        last_target = target;
        if (typeof target === "function") target = target();
      }
      if (delta.constant) {
        data = delta.data;
      } else {
        data = ko.mapping.fromJS(delta.data);
      }
      switch (delta.event) {
        case "add":
          return last_target.push(data);
        case "change":
        case "set":
          return last_target.replace(last_key, data);
        case "remove":
          return last_target.remove(last_key);
      }
    };

    return Util;

  })();

  ConversationModel = (function() {

    function ConversationModel() {}

    ConversationModel.prototype.name = ko.observable();

    ConversationModel.prototype.messages = ko.observableArray([new Message("someguy", "hi"), new Message("me", "hello")]);

    ConversationModel.prototype.addMessage = function() {
      return this.messages.push(new Message("someguy", "hmmm"));
    };

    return ConversationModel;

  })();

  SessionModel = (function() {

    function SessionModel() {}

    SessionModel.prototype.name = ko.observable();

    return SessionModel;

  })();

  $(function() {
    var _this = this;
    return window.client = new JSONRPCClient({
      url: "ws://127.0.0.1:8000/",
      ready: function() {
        return client.getSession(function(result) {
          console.log("Got: ");
          console.log(result);
          window.session = ko.mapping.fromJS(result);
          return ko.applyBindings(session);
        });
      },
      notification: function(data) {
        var shouldScroll;
        shouldScroll = $(document).scrollTop() === ($(document).height() - $(window).height());
        console.log("Notification: " + data);
        Util.applyDelta(session, data.delta);
        if (shouldScroll) {
          return $(document).scrollTop($(document).height() - $(window).height());
        }
      },
      error: function(e) {
        console.log("Error!");
        throw e;
      }
    });
  });

}).call(this);
