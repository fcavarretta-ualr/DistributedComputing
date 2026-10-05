"""
ntp_clock.py -- the two ingredients of NTP: a clock that ticks, and the estimate of how far off it is.

THE SETTING
-----------
A client wants to know how far its clock is from a server's clock (the server is
assumed to be right). It cannot just ask "what time is it?": the answer takes time to
travel back, so it is already out of date when it arrives. NTP therefore exchanges ONE
request and ONE reply and records four timestamps:

    T0C   client clock when the client SENDS the request
    T1S   server clock when the server RECEIVES the request
    T2S   server clock when the server SENDS the reply
    T3C   client clock when the client RECEIVES the reply

(the notation of the slides: superscript C = read on the client's clock, S = read on
the server's clock).

THE ESTIMATE
------------
delta (round-trip delay):  how long the messages spent travelling, in total.
        delta = ((T3C - T0C) - (T2S - T1S)) / 2
    T3C - T0C is the whole exchange as the client saw it; T2S - T1S is the time the
    server kept the request. What is left is the time on the network, halved to get
    the one-way delay.

theta (time difference):  how far the client's clock is from the server's.
        theta = ((T1S - T0C) + (T2S - T3C)) / 2
    T1S - T0C = theta + delay of the request;  T2S - T3C = theta - delay of the reply.
    Adding the two cancels the delays IF request and reply took the same time.
    theta > 0: the client is BEHIND the server and must move forward by theta.
    theta < 0: the client is AHEAD of the server.

THE CLOCK
---------
A real clock is a counter that an interrupt increments at every tick: it does not
change continuously, it jumps by `tick_increment` each time the timer fires. Here the
timer is a BACKGROUND THREAD: it sleeps for `period` seconds, adds `tick_increment` to
the counter, and starts again, while the rest of the program (the NTP protocol) runs
undisturbed in the main thread and just READS the counter when it needs the time.

REALIGNING
----------
When the client learns that it is off by theta, it does not set its clock to the new
value: a jump could make time run backward or repeat. Instead realign(theta, cycles)
asks the clock thread to add theta/cycles on top of the normal tick_increment at each of
the next `cycles` ticks, so the clock catches up gradually.

If theta is positive (the clock is behind) this always takes exactly `cycles` ticks. If
theta is negative (the clock is ahead) the clock has to run SLOWER, but it must never run
backward: a tick may take away at most tick_increment, so the clock stands still for a
few ticks, and a large negative theta takes more than `cycles` ticks to absorb.
"""
import threading
import time


class TickClock:
    """A software clock: a counter that a background thread increments at every tick.

    Parameters
    ----------
    start : number
        The value the clock shows at the very beginning (its "time of day" at start-up).
        The server starts at 1000; the client starts at 1000 minus the --difference given
        on the command line, which is how the two clocks begin out of step.
    tick_increment : number
        How much the counter grows at each tick, in clock units. It is the RESOLUTION of
        the clock: a clock with tick_increment 2 can only show even steps, so a reading can
        be up to 2 units older than the real time.
    period : number
        Real seconds between two ticks: the argument of the sleep in the clock thread. How
        often the counter is updated.
    on_tick : function(value), optional
        Called by the clock thread right after every tick with the new value. Here it is
        used to record the tick in the event log; the clock itself does not need it.

    tick_increment and period together set the SPEED of the clock: it gains
    tick_increment / period clock units per real second. Server: 2 / 2 = 1 unit per second.
    Client: 1 / 1 = 1 unit per second. Equal speeds, so the difference between the two clocks
    stays constant until the client realigns.
    """

    def __init__(self, start, tick_increment, period, on_tick=None):
        self.value = start                    # what the clock shows now
        self.tick_increment = tick_increment  # how much one tick adds
        self.period = period                  # real seconds between two ticks (the sleep)
        self.on_tick = on_tick                # optional callback(value), called after each tick
        self._share = 0                       # correction added at each tick while realigning
        self._remaining = 0                   # part of theta still to be added (0 = not realigning)
        self._lock = threading.Lock()         # the counter is shared by two threads: take the lock to touch it
        self._stop = threading.Event()        # set by stop() to tell the clock thread to finish
        self._thread = threading.Thread(target=self._run, daemon=True)   # the clock thread (not started yet)

    # ---- the background thread ----------------------------------------------------------
    def _run(self):
        """The clock thread: wait one period, tick, repeat until stop() is called."""
        # Event.wait(period) sleeps for `period` seconds and returns False; if stop() is called
        # meanwhile it returns True at once, which ends the loop.
        while not self._stop.wait(self.period):
            with self._lock:                          # no other thread may read the value mid-update
                step = self.tick_increment            # a normal tick adds tick_increment
                if abs(self._remaining) > 1e-9:       # a realignment is in progress
                    # Add one share of the correction (or what is left of it, if that is
                    # smaller), but never let the tick add less than 0: the clock may stand
                    # still, but it must not run backward.
                    share = self._share
                    if abs(share) > abs(self._remaining):
                        share = self._remaining       # the last share: only what is left
                    share = max(share, -self.tick_increment)   # a negative share is limited
                    self._remaining -= share          # this much of the correction is done
                    step += share                     # the tick adds the normal increment plus the share
                self.value += step                    # the tick itself
                value = self.value                    # remember the new value for the callback
            if self.on_tick:                          # outside the lock: the callback may read the clock
                self.on_tick(value)

    def start(self):
        """Start the clock thread: from now on the clock ticks in the background."""
        self._thread.start()

    def stop(self):
        """Stop the clock thread and wait until it has finished."""
        self._stop.set()                              # wakes the thread up and ends its loop
        self._thread.join()

    # ---- used by the main thread --------------------------------------------------------
    def read(self):
        """The time shown by the clock right now."""
        with self._lock:                              # never read in the middle of a tick
            return self.value

    def realign(self, theta, cycles):
        """Spread a correction of `theta` over the next `cycles` ticks."""
        with self._lock:
            self._share = theta / cycles              # the part added at each tick
            self._remaining = theta                   # the clock thread counts it down


def estimate(t0c, t1s, t2s, t3c):
    """Return (theta, delta) from the four timestamps of one request/reply exchange."""
    # delta: whole exchange as the client saw it, minus the time the server kept the request,
    # halved to get the one-way delay.
    delta = ((t3c - t0c) - (t2s - t1s)) / 2
    # theta: the two one-way differences (server clock minus client clock, each including one
    # network delay, with opposite signs), averaged so that the delays cancel.
    theta = ((t1s - t0c) + (t2s - t3c)) / 2
    return theta, delta
