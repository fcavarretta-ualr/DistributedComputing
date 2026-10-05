"""
lamport_clock.py -- the Lamport logical clock of ONE process.

WHAT IS A LAMPORT CLOCK?
------------------------
Physical clocks drift, so wall-clock time cannot be trusted to order events on
different machines. Lamport's idea is to forget about time and COUNT EVENTS:
every process keeps ONE integer counter C that is bumped whenever something
happens. The value has no meaning by itself; it only serves to order events.

THE RULES (the same three rules as on the "Lamport's Algorithm" slide)
----------------------------------------------------------------------
The counter starts at 0.

  1. Before executing an event, P_i increments its counter:      C += 1
  2. When P_i sends a message m, it attaches the new counter value as the
     timestamp ts(m). Sending is itself an event, so rule 1 applies first.
  3. When P_j receives m, it fast-forwards its counter if it is behind:
         C = max(C, ts(m))
     and then counts the receive as an event (rule 1).

WHAT IT GUARANTEES, AND WHAT IT DOES NOT
----------------------------------------
    a -> b  (a happened-before b)    implies    C(a) < C(b)
    C(a) < C(b)                      does NOT imply   a -> b

Two events in processes that never communicate can still get C(a) < C(b) by
coincidence, so one counter cannot tell "before" from "unrelated". Vector clocks
(vector_clock.py) keep one counter per process and remove that limitation.
"""


class LamportClock:

    def __init__(self):
        self.counter = 0

    def tick(self):
        """
        Rule 1 (and rule 2): a local event, or the send of a message.

        Returns the new counter. To SEND a message, call tick() and ship the
        returned value as ts(m): sending is just an event whose counter is
        attached to the message.
        """
        self.counter += 1
        return self.counter

    def receive(self, ts):
        """
        Rule 3: receive a message stamped `ts`.

        The max() fast-forwards a clock that is behind the sender's, so the
        receive can never get a smaller number than the send it depends on.
        The receive itself is then counted as an event, which keeps it strictly
        larger than the send.
        """
        self.counter = max(self.counter, ts)
        return self.tick()
