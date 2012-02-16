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
    test("subscribe all", function() {
      var alerter, subscription;
      alerter = new Alerter();
      subscription = alerter.subscribe("__all__", callback);
      alerter.alert();
      deepEqual(callbackResult, [null, "alert", "Alert!"]);
      alerter.warn();
      return deepEqual(callbackResult, [null, "warn", "Warning!"]);
    });
    test("unsubscribe", function() {
      var alerter, subscription;
      alerter = new Alerter();
      subscription = alerter.subscribe("alert", callback);
      alerter.unsubscribe(subscription);
      alerter.alert();
      return equal(callbackResult, null);
    });
    test("subscription cancel", function() {
      var alerter, subscription;
      alerter = new Alerter();
      subscription = alerter.subscribe("alert", callback);
      subscription.cancel();
      alerter.alert();
      return equal(callbackResult, null);
    });
    test("propagation", function() {
      var SuperAlerter, subscription, super_alerter;
      SuperAlerter = (function(_super) {

        __extends(SuperAlerter, _super);

        function SuperAlerter(alerter, alerter2) {
          this.alerter = alerter;
          this.alerter2 = alerter2;
        }

        return SuperAlerter;

      })(SimpleObservable);
      super_alerter = new SuperAlerter(new Alerter(), new Alerter());
      subscription = super_alerter.subscribe("__all__", callback);
      super_alerter.alerter2.alert();
      return deepEqual(callbackResult, [["alerter2", null], "alert", "Alert!"]);
    });
    return test("garbage collection", function() {
      var ParanoidAlerter, paranoid_alerter, status, subscription;
      status = {
        "deleted": false
      };
      ParanoidAlerter = (function(_super) {

        __extends(ParanoidAlerter, _super);

        function ParanoidAlerter() {
          ParanoidAlerter.__super__.constructor.apply(this, arguments);
        }

        ParanoidAlerter.prototype.__del__ = function() {
          return this.status["deleted"] = true;
        };

        return ParanoidAlerter;

      })(SimpleObservable);
      paranoid_alerter = new ParanoidAlerter();
      paranoid_alerter.status = status;
      paranoid_alerter.child = new Alerter();
      subscription = paranoid_alerter.subscribe("__all__", callback);
      deepEqual(paranoid_alerter._subscribers["__all__"], [subscription]);
      notDeepEqual(paranoid_alerter.child._subscribers["__all__"], []);
      subscription.cancel();
      delete subscription;
      deepEqual(paranoid_alerter._subscribers, {});
      deepEqual(paranoid_alerter._subscriptions, []);
      deepEqual(paranoid_alerter.child._subscribers, {});
      return delete paranoid_alerter;
    });
  });

}).call(this);
