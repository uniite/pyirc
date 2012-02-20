(function() {
  var ObservableList, SimpleObservable, Subscription,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

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

    SimpleObservable.prototype.addSubscription = function(observable, event, prefix) {
      var ourCallback,
        _this = this;
      event || (event = "__all__");
      this._subscriptions || (this._subscriptions = []);
      if (typeof observable.isObservable === "function" ? observable.isObservable() : void 0) {
        ourCallback = function(t, e, d) {
          return _this._notify(t, e, d);
        };
        return this._subscriptions.push(observable.subscribe(event, ourCallback, void 0, prefix));
      }
    };

    SimpleObservable.prototype.removeSubscriptions = function(observable, cancel) {
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

  ObservableList = (function(_super) {

    __extends(ObservableList, _super);

    function ObservableList() {
      this.subscribe = __bind(this.subscribe, this);
      this.push = __bind(this.push, this);
      this.insert = __bind(this.insert, this);
      var v, _i, _len;
      this.list = [];
      for (_i = 0, _len = arguments.length; _i < _len; _i++) {
        v = arguments[_i];
        this.list.push(v);
      }
    }

    ObservableList.prototype.length = function() {
      return this.list.length;
    };

    ObservableList.prototype.__getitem__ = function(i) {
      return this.list[i];
    };

    ObservableList.prototype.remove = function(item_to_remove) {
      var i, v, _len, _ref, _results;
      _ref = this.list;
      _results = [];
      for (i = 0, _len = _ref.length; i < _len; i++) {
        v = _ref[i];
        if (v === item_to_remove) {
          this._notify(i, "remove", v);
          this.removeSubscriptions(v);
          this.list.slice(i, i + 1);
          break;
        } else {
          _results.push(void 0);
        }
      }
      return _results;
    };

    ObservableList.prototype._setitem__ = function(i, v) {
      this._notify(i, "change", v);
      this.removeSubscriptions(this.list[i]);
      this.addSubscription(v, i);
      return this.list[i] = v;
    };

    ObservableList.prototype.insert = function(i, v) {
      this._notify(i, "add", v);
      this.addSubscription(v, void 0, i);
      return this.list.splice(i, 1, v);
    };

    ObservableList.prototype.push = function(v) {
      return this.insert(this.list.length, v);
    };

    ObservableList.prototype.toString = function() {
      return this.list.toString();
    };

    ObservableList.prototype.toDict = function() {
      return this.list;
    };

    ObservableList.prototype.subscribe = function(event, callback, shared, prefix) {
      var i, item, ourCallback, _ref,
        _this = this;
      this._subscriptions || (this._subscriptions = []);
      if (this._subscriptions.length === 0) {
        for (i = 0, _ref = this.list.length; 0 <= _ref ? i <= _ref : i >= _ref; 0 <= _ref ? i++ : i--) {
          item = this.list[i];
          if (item != null ? typeof item.isObservable === "function" ? item.isObservable() : void 0 : void 0) {
            ourCallback = function(t, e, d) {
              return _this._notify(t, e, d);
            };
            this._subscriptions.push(item.subscribe("__all__", ourCallback, true, i));
          }
        }
      }
      return ObservableList.__super__.subscribe.call(this, event, callback, shared, prefix);
    };

    return ObservableList;

  })(SimpleObservable);

  window.SimpleObservable = SimpleObservable;

  window.ObservableList = ObservableList;

}).call(this);
