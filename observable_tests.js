(function() {
  var __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  $(function() {
    var Alerter, callback, callbackResult, multiCallback;
    Alerter = (function(_super) {

      __extends(Alerter, _super);

      function Alerter() {
        Alerter.__super__.constructor.apply(this, arguments);
      }

      Alerter.prototype.alert = function() {
        return this._notify(null, "alert", "Alert!");
      };

      Alerter.prototype.warn = function() {
        return this._notify(null, "warn", "Warning!");
      };

      return Alerter;

    })(SimpleObservable);
    callbackResult = null;
    QUnit.testStart(function() {
      return callbackResult = null;
    });
    callback = function(t, e, d) {
      if (d != null) {
        return callbackResult = [t, e, d];
      } else {
        return callbackResult = [t, e];
      }
    };
    multiCallback = function(t, e, d) {
      callbackResult || (callbackResult = []);
      if (d != null) {
        return callbackResult.push([t, e, d]);
      } else {
        return callbackResult.push([t, e]);
      }
    };
    test("subscribe", function() {
      var alerter, k, subscription, v;
      expect(8);
      alerter = new Alerter();
      subscription = alerter.subscribe("alert", callback);
      for (k in subscription) {
        v = subscription[k];
        equal(alerter._subscribers["alert"][0][k], v);
      }
      alerter.alert();
      equal(callbackResult.length, 2);
      equal(callbackResult[1], "Alert!");
      return;
    });
    test("susbcribe multiple", function() {
      var alerter, i, _results;
      alerter = new Alerter();
      for (i = 1; i <= 3; i++) {
        alerter.subscribe("alert", multiCallback);
      }
      alerter.alert();
      equal(callbackResult.length, 3);
      _results = [];
      for (i = 0; i <= 2; i++) {
        _results.push(deepEqual(callbackResult[i], [null, "Alert!"]));
      }
      return _results;
    });
    return test("subscribe all", function() {
      var alerter, subscription;
      alerter = new Alerter();
      subscription = alerter.subscribe("__all__", callback);
      alerter.alert();
      deepEqual(callbackResult, [null, "alert", "Alert!"]);
      alerter.warn();
      return deepEqual(callbackResult, [null, "warn", "Warning!"]);
    });
  });

}).call(this);
