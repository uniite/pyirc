(function() {
  var JSONRPCClient, Message, SessionModel, Util,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

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
        console.log("RESPONSE " + e.data);
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

  SessionModel = (function() {

    function SessionModel(data) {
      this.openConversation = __bind(this.openConversation, this);
      this.sendMessage = __bind(this.sendMessage, this);
      var _this = this;
      ko.mapping.fromJS(data, {}, this);
      this.currentConversationIndex = ko.observable(0);
      this.outgoingMessage = ko.observable("");
      this.currentConversation = ko.computed(function() {
        return _this.conversations()[_this.currentConversationIndex()];
      });
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
      return scrollNext();
    };

    return SessionModel;

  })();

  $(window).resize(function() {
    reformat();
    return window.scrollSnap();
  });

  $(document).bind("scroll", function() {
    if (window.scrollDone === true) {
      window.scrollDone = false;
      return;
    }
    if (window.scrollStopTimeout) clearTimeout(window.scrollStopTimeout);
    window.scrollStopTimeout = setTimeout(window.scrollSnap, 100);
    return true;
  });

  window.scrollSnapEnabled = true;

  window.scrollNext = function() {
    return scrollToPane(currentPane() + 1);
  };

  window.currentPane = function() {
    return $("body").scrollLeft() / $(window).width();
  };

  window.scrollToPane = function(pane) {
    var targetX;
    targetX = $(window).width() * pane;
    $("body").stop(true, true);
    return $("body").animate({
      scrollLeft: targetX
    }, {
      duration: 200
    });
  };

  window.scrollSnap = function() {
    var closerToLeft, leftPaneX, rightPaneX, scrollX, targetX, windowWidth;
    if (!window.scrollSnapEnabled) return;
    console.warn("Snap!");
    windowWidth = $(window).width();
    scrollX = $(window).scrollLeft();
    leftPaneX = Math.floor(scrollX / windowWidth) * windowWidth;
    rightPaneX = leftPaneX + windowWidth;
    closerToLeft = ((scrollX - leftPaneX) - (windowWidth / 2)) < 0;
    if (closerToLeft) {
      targetX = leftPaneX;
    } else {
      targetX = rightPaneX;
    }
    if (Math.abs(scrollX - targetX) < 10) {
      $("body").scrollLeft(targetX);
    } else {
      scrollToPane(targetX / windowWidth);
    }
    return window.reformat();
  };

  window.reformat = function() {
    var windowWidth;
    windowWidth = $(window).width();
    $(".footer .inner-left").width(windowWidth - $(".footer .inner-right").width());
    window.scrollSnapThreshold = windowWidth / 2;
    return true;
  };

  $(function() {
    var _this = this;
    $(window).bind("touchdown", function(e) {
      $("body").stop(true, false);
      return true;
    });
    $(window).bind("touchstart", function(e) {
      $("body").stop(true, false);
      return true;
    });
    $(window).bind("touchmove", function(e) {
      $("body").stop(true, false);
      return true;
    });
    window.reformat();
    return window.client = new JSONRPCClient({
      url: "ws://192.168.7.100:8000/",
      ready: function() {
        console.log("Ready callback");
        return client.getSession(function(result) {
          console.log("Got Session");
          window.session = new SessionModel(result);
          ko.applyBindings(window.session);
          $(document).scrollLeft(0);
          return window.reformat();
        });
      },
      notification: function(data) {
        console.log("Notification: " + data);
        return Util.applyDelta(session, data.delta);
      },
      error: function(e) {
        console.log("Error: " + JSON.stringify(e));
        throw e;
      }
    });
  });

}).call(this);
