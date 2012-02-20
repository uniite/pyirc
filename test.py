__author__ = 'Jon'

import unittest
from observable import SimpleObservable, ObservableList, ObservableDict

class TestSimpleObservable(unittest.TestCase):
    def setUp(self):
        self.callback_result = None

    class Alerter(SimpleObservable):
        def alert(self):
            self._notify(None, "alert", "Alert!")
        def warn(self):
            self._notify(None, "warn", "Warning!")

    def callback(self, *args):
        self.callback_result = args

    def multi_callback(self, *args):
        if not self.callback_result:
            self.callback_result = []
        self.callback_result.append(args)


    def test_subscribe(self):
        # Create an observable
        alerter = self.Alerter()
        # Subscribe to its alert event
        subscription = alerter.subscribe("alert", self.callback)
        # Make sure the subscription is there
        self.assertEqual([subscription], alerter._subscribers["alert"])
        # Trigger an event
        alerter.alert()
        # Make sure it called the callback
        self.assertEqual((None, "Alert!"), self.callback_result)

    def test_shared_subscribe(self):
        # Create an observable
        alerter = self.Alerter()
        # Subscribe to its alert and warn events
        subscription = alerter.subscribe("alert", self.callback, True)
        subscription = alerter.subscribe("warn", self.callback, True)
        # Trigger an event
        alerter.alert()
        # Make sure it called the callback
        self.assertEqual((None, "alert", "Alert!"), self.callback_result)
        # Trigger another event
        alerter.warn()
        # Make sure it called the callback
        self.assertEqual((None, "warn", "Warning!"), self.callback_result)

    def test_subscribe_multiple(self):
        # Create an observable
        alerter = self.Alerter()
        # Subscribe to its alert event thrice
        for i in range(3):
            alerter.subscribe("alert", self.multi_callback)
        # Trigger an event
        alerter.alert()
        # Make sure it called the callback thrice
        self.assertEqual([(None, "Alert!")] * 3, self.callback_result)

    def test_subscribe_all(self):
        # Create an observable
        alerter = self.Alerter()
        # Subscribe to everything
        subscription = alerter.subscribe("__all__", self.callback)
        # Trigger an event
        alerter.alert()
        # Make sure it called the callback
        self.assertEqual((None, "alert", "Alert!"), self.callback_result)
        # Trigger another event
        alerter.warn()
        # Make sure it called the callback
        self.assertEqual((None, "warn", "Warning!"), self.callback_result)

    def test_unsubscribe(self):
        # Create an observable
        alerter = self.Alerter()
        # Subscribe to its alert event
        subscription = alerter.subscribe("alert", self.callback)
        # Unsubscribe via the observable
        alerter.unsubscribe(subscription)
        # Trigger an event
        alerter.alert()
        # Make sure it didn't call the callback
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

    def test_propagation(self):
        # Create an observable that contains an observable
        class SuperAlerter(SimpleObservable):
            def __init__(self, alerter, alerter2):
                self.alerter = alerter
                self.alerter2 = alerter2
        super_alerter = SuperAlerter(self.Alerter(), self.Alerter())
        # Subscribe to everything
        subscription = super_alerter.subscribe("__all__", self.callback)
        # Trigger an event on the second Alerter
        super_alerter.alerter2.alert()
        # Make sure it propagated via super_alerter, with the right prefix
        self.assertEqual((("alerter2", None), "alert", "Alert!"), self.callback_result)

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
        subscription = paranoid_alerter.subscribe("__all__", self.callback)
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


class TestObservableList(unittest.TestCase):
    def setUp(self):
        self.callback_result = None

    def callback(self, *args):
        self.callback_result = args

    def test_add(self):
        # Create an observable list
        observable_list = ObservableList()
        # Subscribe to add events
        subscription = observable_list.subscribe("add", self.callback)
        # Add an item to it
        observable_list.append("nom")
        # Ensure this triggered the callback
        self.assertEqual((0, "nom"), self.callback_result)

    def test_remove(self):
        # Create an observable dict
        observable_list = ObservableList("one", "of", "these", "things")
        # Subscribe to remove events
        subscription = observable_list.subscribe("remove", self.callback)
        # Remove an item from it
        del observable_list[2]
        # Ensure this triggered the callback
        self.assertEqual((2, "these"), self.callback_result)

    def test_change(self):
        # Create an observable dict
        observable_list = ObservableList("something", "might", "change")
        # Subscribe to change events
        subscription = observable_list.subscribe("change", self.callback)
        # Change an item in it
        observable_list[1] = "will"
        # Ensure this triggered the callback
        self.assertEqual((1, "will"), self.callback_result)

    def test_propagation(self):
        class Alerter(SimpleObservable):
            def alert(self):
                self._notify(None, "alert", "Alert!")
        # Create an observable list that contains other observables
        observable_list = ObservableList(Alerter(), Alerter())
        # Subscribe to all events
        subscription = observable_list.subscribe("__all__", self.callback)
        # Trigger an alert on something in the list
        observable_list[1].alert()
        # Ensure this triggered the callback
        self.assertEqual(((1, None), "alert", "Alert!"), self.callback_result)

    def test_double_propagation(self):
        class MiddleMan(SimpleObservable):
            def __init__(self):
                self.children = ObservableList()
        # Create an observable list in an observable in an onbservable list
        parent = ObservableList()
        # Subscribe to the to-level list
        parent.subscribe("__all__", self.callback)
        # Add something to it
        middle_man = MiddleMan()
        parent.append(middle_man)
        # Ensure this tells us the item was added at index 0 of the top-level
        self.assertEqual((0, "add", middle_man), self.callback_result)
        # Add a few things to the inner list
        middle_man.children.append("hi!")
        middle_man.children.append("hello!")
        # Ensure we get told the string was added at parent[0].children[0]
        self.assertEqual(((0, "children", 1), "add", "hello!"), self.callback_result)

    def test_str(self):
        self.assertEqual(str([1, 2, 3]), "%s" % ObservableList(1, 2, 3))

    def test_to_dict(self):
        self.assertEqual([1, 2, 3], ObservableList(1, 2, 3).to_dict())



class TestObservableDict(unittest.TestCase):
    def setUp(self):
        self.callback_result = None

    def callback(self, *args):
        self.callback_result = args

    def test_add(self):
        # Create an observable dict
        observable_dict = ObservableDict()
        # Subscribe to add events
        subscription = observable_dict.subscribe("add", self.callback)
        # Add an item to it
        observable_dict["foo"] = "bar"
        # Ensure this triggered the callback
        self.assertEqual(("foo", "bar"), self.callback_result)

    def test_remove(self):
        # Create an observable dict
        observable_dict = ObservableDict({"good": "bye"})
        # Subscribe to remove events
        subscription = observable_dict.subscribe("remove", self.callback)
        # Remove an item from it
        del observable_dict["good"]
        # Ensure this triggered the callback
        self.assertEqual(("good", "bye"), self.callback_result)

    def test_change(self):
        # Create an observable dict
        observable_dict = ObservableDict({"good": "bye"})
        # Subscribe to change events
        subscription = observable_dict.subscribe("change", self.callback)
        # Change an item in it
        observable_dict["good"] = "morning"
        # Ensure this triggered the callback
        self.assertEqual(("good", "morning"), self.callback_result)

    def test_propagation(self):
        class Alerter(SimpleObservable):
            def alert(self):
                self._notify(None, "alert", "Alert!")
        # Create an observable dict that contains other observables
        observable_dict = ObservableDict({
            "this": Alerter(),
            "that": Alerter()
        })
        # Subscribe to all events
        subscription = observable_dict.subscribe("__all__", self.callback)
        # Trigger an alert on something in the dict
        observable_dict["that"].alert()
        # Ensure this triggered the callback
        self.assertEqual((("that", None), "alert", "Alert!"), self.callback_result)



if __name__ == '__main__':
    unittest.main()
