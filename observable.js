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
      return this.observable.unsubscribe(self);
    };

    return Subscription;

  })();

  SimpleObservable = (function() {

    function SimpleObservable() {}

    SimpleObservable.prototype.isObservable = function() {
      return true;
    };

    SimpleObservable.prototype._notify = function(target, event, data) {
      var s, _base, _base2, _i, _len, _ref, _results;
      if (this._subscribers == null) return;
      (_base = this._subscribers)[event] || (_base[event] = []);
      (_base2 = this._subscribers)["__all__"] || (_base2["__all__"] = []);
      _ref = $.merge(this._subscribers[event] || [], this._subscribers["__all__"] || []);
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        s = _ref[_i];
        if (s.shared) {
          if (s.prefix != null) {
            if (!target.push) target = [target];
            _results.push(s.callback([s.prefix] + target, event, data));
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
      var k, s, v, _base, _len;
      if (!(self._subscriptions != null)) {
        this._subscriptions = [];
        for (v = 0, _len = this.length; v < _len; v++) {
          k = this[v];
          if (typeof v.isObservable === "function" ? v.isObservable() : void 0) {
            this._subscriptions.push(v.subscribe("__all__", this._notify, true, k));
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
      var s, _i, _len, _ref;
      this._subscribers[subscription.event].remove(subscription);
      if (this._subscribers[subscription.event] === []) {
        delete self._subscribers[subscription.event];
      }
      if (self._subscribers === {}) {
        _ref = self._subscriptions;
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
