__author__ = 'Jon'

import unittest
from observable import SimpleObservable

class TestSimpleObservable(unittest.TestCase):
    def setUp(self):
        self.callback_result = None

    class Alerter(SimpleObservable):
        def alert(self):
            self._notify("alert", "Alert!", level="important")
        def warn(self):
            self._notify("warn", "Warning!", level="meh")

    def callback(self, msg, level=None):
        self.callback_result = (msg, level)

    def multi_callback(self, msg, level=None):
        if not self.callback_result:
            self.callback_result = []
        self.callback_result.append((msg, level))

    def shared_callback(self, event, msg, level=None):
        self.callback_result = (event, msg, level)

    def test_subscribe(self):
        # Create an observable
        alerter = self.Alerter()
        # Subscribe to its alert event
        subscription = alerter.subscribe("alert", self.callback)
        # Make sure the subscription is there
        self.assertEqual(alerter._subscribers["alert"], [subscription])
        # Trigger an event
        alerter.alert()
        # Make sure it called the callback
        self.assertEqual(("Alert!", "important"), self.callback_result)

    def test_shared_subscribe(self):
        # Create an observable
        alerter = self.Alerter()
        # Subscribe to its alert and warn events
        subscription = alerter.subscribe("alert", self.shared_callback, True)
        subscription = alerter.subscribe("warn", self.shared_callback, True)
        # Trigger an event
        alerter.alert()
        # Make sure it called the callback
        self.assertEqual(("alert", "Alert!", "important"), self.callback_result)
        # Trigger another event
        alerter.warn()
        # Make sure it called the callback
        self.assertEqual(("warn", "Warning!", "meh"), self.callback_result)

    def test_subscribe_multiple(self):
        # Create an observable
        alerter = self.Alerter()
        # Subscribe to its alert event thrice
        for i in range(3):
            subscription = alerter.subscribe("alert", self.multi_callback)
        # Trigger an event
        alerter.alert()
        # Make sure it called the callback thrice
        self.assertEqual([("Alert!", "important")] * 3, self.callback_result)

    def test_subscribe_all(self):
        # Create an observable
        alerter = self.Alerter()
        # Subscribe to everything
        subscription = alerter.subscribe("__all__", self.shared_callback)
        # Trigger an event
        alerter.alert()
        # Make sure it called the callback
        self.assertEqual(("alert", "Alert!", "important"), self.callback_result)
        # Trigger another event
        alerter.warn()
        # Make sure it called the callback
        self.assertEqual(("warn", "Warning!", "meh"), self.callback_result)

    def test_unsubscribe(self):
        # Create an observable
        alerter = self.Alerter()
        # Subscribe to its alert event
        subscription = alerter.subscribe("alert", self.callback)
        # Unsubscribe via the observable
        alerter.unsubscribe(subscription)
        # Trigger an event
        alerter.alert()
        # Make sure it called the callback
        self.assertEqual(None, self.callback_result)

    def test_subscription_cancel(self):
        # Create an observable
        alerter = self.Alerter()
        # Subscribe to its alert event
        subscription = alerter.subscribe("alert", self.callback)
        # Unsubscribe via the subscription
        subscription.cancel()
        # Trigger an event
        alerter.alert()
        # Make sure it did not call the callback
        self.assertEqual(None, self.callback_result)

    def test_subscription_propagation(self):
        # Create an observable that contains an observable
        class SuperAlerter(SimpleObservable):
            def __init__(self, alerter, alerter2):
                self.alerter = alerter
                self.alerter2 = alerter2
                SimpleObservable.__init__(self)
        super_alerter = SuperAlerter(self.Alerter(), self.Alerter())
        # Subscribe to everything
        subscription = super_alerter.subscribe("__all__", self.shared_callback)
        # Trigger an event on the second Alerter
        super_alerter.alerter2.alert()
        # Make sure it propagated via super_alerter, with the right prefix
        self.assertEqual(("alerter2.alert", "Alert!", "important"), self.callback_result)

    def test_garbage_collection(self):
        status = {"deleted": False}
        class ParanoidAlerter(SimpleObservable):
            def __del__(self):
                self.status["deleted"] = True
        paranoid_alerter = ParanoidAlerter()
        paranoid_alerter.status = status
        # Give it a child observable to subscribe to
        paranoid_alerter.child = self.Alerter()
        # Give it a subscription
        subscription = paranoid_alerter.subscribe("__all__", self.shared_callback)
        # Make sure it sticks
        self.assertEqual([subscription], paranoid_alerter._subscribers.values()[0])
        self.assertNotEqual([], paranoid_alerter.child._subscribers.values())
        # Cancel and delete the subscription to remove all references to it
        subscription.cancel()
        del subscription
        # Ensure the subscriptions are all cleaned up
        self.assertEqual({}, paranoid_alerter._subscribers)
        self.assertEqual([], paranoid_alerter._subscriptions)
        self.assertEqual({}, paranoid_alerter.child._subscribers)
        # Ensure paranoid_alerter can now be garbage collected
        del paranoid_alerter
        self.assertTrue(status["deleted"])



if __name__ == '__main__':
    unittest.main()
