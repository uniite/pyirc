(function() {
  var ConversationModel, JSONRPCClient, Message, SynchronizedModel,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

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

  SynchronizedModel = (function() {

    function SynchronizedModel() {
      this.onDelta = __bind(this.onDelta, this);
    }

    SynchronizedModel.prototype.onDelta = function(data) {
      var item, key, newData, value, _results;
      console.log(data);
      _results = [];
      for (key in data) {
        value = data[key];
        if (this[key].push) {
          newData = {};
          newData[key] = value;
          _results.push((function() {
            var _i, _len, _ref, _results2;
            _ref = ko.mapping.fromJS(newData)[key]();
            _results2 = [];
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              item = _ref[_i];
              _results2.push(this[key].push(item));
            }
            return _results2;
          }).call(this));
        } else {
          _results.push(this[key](value));
        }
      }
      return _results;
    };

    return SynchronizedModel;

  })();

  ConversationModel = (function(_super) {

    __extends(ConversationModel, _super);

    function ConversationModel() {
      ConversationModel.__super__.constructor.apply(this, arguments);
    }

    ConversationModel.prototype.name = ko.observable();

    ConversationModel.prototype.messages = ko.observableArray([new Message("someguy", "hi"), new Message("me", "hello")]);

    ConversationModel.prototype.addMessage = function() {
      return this.messages.push(new Message("someguy", "hmmm"));
    };

    return ConversationModel;

  })(SynchronizedModel);

  $(function() {
    var _this = this;
    window.client = new JSONRPCClient({
      url: "ws://127.0.0.1:8000/",
      ready: function() {
        return client.getMessages(function(result) {
          console.log("Got: " + result);
          return ko.mapping.fromJS({
            messages: result
          }, {}, conversation);
        });
      },
      notification: function(data) {
        var shouldScroll;
        shouldScroll = $(document).scrollTop() === ($(document).height() - $(window).height());
        console.log("Notification: " + data);
        conversation.onDelta({
          messages: data
        });
        if (shouldScroll) {
          return $(document).scrollTop($(document).height() - $(window).height());
        }
      },
      error: function(e) {
        console.log("Error!");
        throw e;
      }
    });
    window.conversation = new ConversationModel;
    return ko.applyBindings(conversation);
  });

}).call(this);
