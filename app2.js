(function() {
  var JSONRPCClient, SessionModel, Util,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  if (!(window.WebSocket != null) && (window.MozWebSocket != null)) {
    window.WebSocket = window.MozWebSocket;
  }

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
      this.ws.onclose = this.options.error;
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

  Util = (function() {

    function Util() {}

    Util.applyDelta = function(target, delta) {
      var data, key, last_key, last_target, _i, _len, _ref;
      last_key = delta.target.pop();
      _ref = delta.target;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        key = _ref[_i];
        target = target[key];
        last_target = target;
        if (typeof target === "function") target = target();
      }
      data = delta.data;
      switch (delta.event) {
        case "add":
          return last_target.push(data);
        case "change":
        case "set":
          return last_target[last_key] = data;
        case "remove":
          return last_target._remove(last_key);
      }
    };

    return Util;

  })();

  SessionModel = (function() {

    function SessionModel(data) {
      this.openConversation = __bind(this.openConversation, this);
      this.sendMessage = __bind(this.sendMessage, this);
      var c, _i, _len, _ref;
      this.conversations = data.conversations;
      _ref = this.conversations;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        c = _ref[_i];
        c.messages = new ObservableList(c.messages);
        c.users = new ObservableList(c.users);
      }
      this.conversations = new ObservableList(this.conversations);
    }

    SessionModel.prototype.sendMessage = function() {
      var index;
      index = this.conversations().indexOf(this.currentConversation());
      window.client.sendMessage(index, this.outgoingMessage());
      return this.outgoingMessage("");
    };

    SessionModel.prototype.openConversation = function(conversation) {
      var index, start;
      index = conversation.index();
      start = (new Date).getTime();
      index = this.currentConversationIndex(index);
      console.log("TOOK " + ((new Date).getTime() - start));
      autoScrollMessages();
      return scrollNext();
    };

    return SessionModel;

  })();

  $(window).resize(function() {
    return reformat();
  });

  window.messagesScrolledToBottom = function() {
    var scrollContainer, scrollTarget;
    scrollContainer = $("#ConversationInner");
    scrollTarget = $("#MessagesList");
    return scrollContainer.scrollTop() === (scrollTarget.height() - scrollContainer.height());
  };

  window.autoScrollMessages = function() {
    var scrollContainer, scrollTarget;
    scrollContainer = $("#ConversationInner");
    scrollTarget = $("#MessagesList");
    return scrollContainer.scrollTop(scrollTarget.height() - scrollContainer.height());
  };

  window.reformat = function() {
    var windowWidth;
    windowWidth = $(window).width();
    $(".footer .inner-left").width(windowWidth - $(".footer .inner-right").width());
    autoScrollMessages();
    return true;
  };

  $(function() {
    var _this = this;
    window.reformat();
    return window.client = new JSONRPCClient({
      url: "ws://192.168.7.100:8000/",
      ready: function() {
        var rpcStart;
        console.log("Ready callback");
        rpcStart = (new Date).getTime();
        return client.getSession(function(result) {
          var rpcEnd, start;
          rpcEnd = (new Date).getTime() - rpcStart;
          $("#JSONTime").text("Global: " + rpcEnd + "ms");
          console.log("Got Session");
          start = (new Date).getTime();
          window.session = new SessionModel(result);
          $("#UsersListInner").hide();
          $("#UsersListInner").bindToObservable({
            observable: session.conversations[1].messages,
            template: Handlebars.compile($("#MessageItem").html())
          });
          console.log("PROCESS " + ((new Date).getTime() - start));
          return window.setTimeout(function() {
            var end;
            $("#UsersListInner").show();
            end = (new Date).getTime() - start;
            return $("#RenderTime").text("Render: " + end + "ms");
          }, 0);
        });
      },
      notification: function(data) {
        var shouldScroll;
        console.log("Notification: " + data);
        shouldScroll = messagesScrolledToBottom();
        Util.applyDelta(session, data.delta);
        if (shouldScroll) return autoScrollMessages();
      },
      error: function(e) {
        console.log("Error: " + JSON.stringify(e));
        throw e;
      }
    });
  });

}).call(this);
