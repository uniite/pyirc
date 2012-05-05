#! /usr/bin/env python

# BUGS
# - Subscription.cancel on ws_server fails
# - Message body: UnicodeDecodeError: 'utf8' codec can't decode byte 0x95 in position 0: invalid start byte

import gevent.monkey
gevent.monkey.patch_all()

from gevent import Greenlet, sleep
from models.session import Session


def spam(session):
    i = 0
    while True:
        i += 1
        session.recv_message({}, "spambot", "SPAM %s" % i, "testchat")
        sleep(0.05)

def main():
    session = Session()
    session_greenlet = Greenlet.spawn(session.start)
    session_greenlet.join()

if __name__ == "__main__":
    main()