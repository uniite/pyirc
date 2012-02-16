(function() {
  var SimpleObservable, Subscription;

  Subscription = (function() {

    function Subscription(callback, observable, event, shared, prefix) {
      this.callback = callback;
      this.observable = observable;
      this.event = event;
      this.shared = shared;
      this.prefix = prefix;
    }

    Subscription.prototype.cancel = function() {
      return this.observable.unsubscribe(this);
    };

    return Subscription;

  })();

  SimpleObservable = (function() {

    function SimpleObservable() {}

    SimpleObservable.prototype.isObservable = function() {
      return true;
    };

    SimpleObservable.prototype._notify = function(target, event, data) {
      var new_target, s, _base, _base2, _i, _len, _ref, _results;
      if (this._subscribers == null) return;
      (_base = this._subscribers)[event] || (_base[event] = []);
      (_base2 = this._subscribers)["__all__"] || (_base2["__all__"] = []);
      _ref = $.extend(this._subscribers[event] || [], this._subscribers["__all__"] || []);
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        s = _ref[_i];
        if (s.shared) {
          if (s.prefix != null) {
            if (!(target != null ? target.push : void 0)) target = [target];
            new_target = $.merge([s.prefix], target);
            _results.push(s.callback(new_target, event, data));
          } else {
            _results.push(s.callback(target, event, data));
          }
        } else {
          _results.push(s.callback(target, data));
        }
      }
      return _results;
    };

    SimpleObservable.prototype.subscribe = function(event, callback, shared, prefix) {
      var k, ourCallback, s, v, _base,
        _this = this;
      if (!(this._subscriptions != null)) {
        this._subscriptions = [];
        for (k in this) {
          v = this[k];
          if (typeof v.isObservable === "function" ? v.isObservable() : void 0) {
            ourCallback = function(t, e, d) {
              return _this._notify(t, e, d);
            };
            this._subscriptions.push(v.subscribe("__all__", ourCallback, true, k));
          }
        }
      }
      s = new Subscription(callback, this, event, shared || event === "__all__", prefix);
      this._subscribers || (this._subscribers = {});
      (_base = this._subscribers)[event] || (_base[event] = []);
      this._subscribers[event].push(s);
      return s;
    };

    SimpleObservable.prototype.unsubscribe = function(subscription) {
      var s, subscribers, _i, _len, _ref;
      subscribers = this._subscribers[subscription.event];
      subscribers.splice(subscribers.indexOf(subscription), 1);
      if (this._subscribers[subscription.event].length === 0) {
        delete this._subscribers[subscription.event];
      }
      if ($.isEmptyObject(this._subscribers)) {
        _ref = this._subscriptions;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          s = _ref[_i];
          s.cancel();
        }
        return this._subscriptions = [];
      }
    };

    SimpleObservable.prototype.add_subscription = function(observable, event, prefix) {
      event || (event = "__all__");
      this._subscriptions || (this._subscriptions = []);
      if (typeof observable.isObservable === "function" ? observable.isObservable() : void 0) {
        return this._subscriptions.push(observable.subscribe(event, this._notify, void 0, prefix));
      }
    };

    SimpleObservable.prototype.remove_subscriptions = function(observable, cancel) {
      var s, subscription, _i, _len, _ref, _results;
      if (typeof observable.isObservable === "function" ? observable.isObservable() : void 0) {
        _ref = [
          (function() {
            var _j, _len, _ref, _results2;
            _ref = this._subscriptions;
            _results2 = [];
            for (_j = 0, _len = _ref.length; _j < _len; _j++) {
              s = _ref[_j];
              if (s.observable === observable) _results2.push(s);
            }
            return _results2;
          }).call(this)
        ];
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          subscription = _ref[_i];
          if (cancel) subscription.cancel();
          _results.push(this._subscriptions.remove(subscription));
        }
        return _results;
      }
    };

    return SimpleObservable;

  })();

  window.SimpleObservable = SimpleObservable;

}).call(this);
