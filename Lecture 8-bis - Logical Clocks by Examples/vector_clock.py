"""
vector_clock.py -- the vector clock of ONE process.

WHAT IS A VECTOR CLOCK?
-----------------------
In a system of n processes, every process P_i keeps a vector VC of n integers:

        VC[j] = k    means    "P_i knows that k events happened in P_j"

* VC[i] (its OWN entry) counts the events of P_i itself.
* Every other entry VC[j] is P_i's best knowledge of how far P_j has gone. That
  knowledge can only travel inside messages, so it is always possibly out of date.

A single Lamport counter squeezes all this into one number and therefore cannot
tell "a happened before b" from "a and b are unrelated". The vector keeps one
counter per process, which is exactly the extra information needed to tell them
apart (two vectors can be compared entry by entry, see vector_test_1.py / vector_test_2.py).

THE RULES (the same three rules as on the "Vector Clock Algorithm" slide)
-------------------------------------------------------------------------
Every process starts with the all-zero vector, e.g. [0, 0, 0].

  1. Before executing an event, P_i increments its OWN entry:     VC[i] += 1
  2. When P_i sends a message m, it attaches a COPY of its WHOLE vector as the
     timestamp ts(m). Sending is itself an event, so rule 1 applies first.
  3. When P_j receives m, it merges the two vectors entry by entry:
         VC[k] = max(VC[k], ts(m)[k])        for EVERY k
     and then counts the receive as an event (rule 1). After the merge, P_j knows
     everything the sender knew when it sent m, i.e. all that causally precedes m.

The class below is exactly these rules: two methods, no messaging, no printing.
Moving the vectors between processes is the job of the program that uses it.
"""


class VectorClock:

    def __init__(self, pid, n):
        # `pid` is the index i of this process in the vector (0 for P1, 1 for P2, ...).
        # It decides WHICH entry is "our own" and therefore which one tick() bumps.
        self.pid = pid
        # One counter per process, all zero: "no event has happened anywhere yet".
        self.counter = [0] * n

    def tick(self):
        """
        Rule 1 -- a local event, or the send of a message (rule 2).

        Increments only our own entry and returns the new vector. To SEND a
        message, call tick() and ship the returned vector as ts(m): sending is
        just an event whose resulting vector is attached to the message.
        """
        self.counter[self.pid] += 1
        # Return a COPY. If we returned self.counter itself, the caller (and the
        # message queue) would hold a reference to our live vector, which keeps
        # changing; the timestamp must stay frozen at the moment of the send.
        return list(self.counter)

    def receive(self, ts):
        """
        Rule 3 -- receive a message that carries the vector `ts`.

        1) merge: for every process k keep the larger of "what I knew" and "what
           the sender knew"; entries only ever grow, never shrink;
        2) count the receive itself as an event (rule 1) and return the result.
        """
        self.counter = [max(mine, theirs) for mine, theirs in zip(self.counter, ts)]
        return self.tick()
