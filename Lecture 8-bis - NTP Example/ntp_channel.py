"""
ntp_channel.py -- the communication line between the client and the server.

A Channel is one end of the line between the two MPI ranks. It does everything the NTP
program needs from the network, so the client and the server only call
channel.send(...) and channel.recv(...):

  * it knows the other end (`peer`), so no rank numbers are needed at the call sites;
  * it draws ONE random delay when it is created (the seed is set just before) and uses
    that same delay for every message it sends and every message it receives;
  * send() sleeps for the delay (the message is "on the wire"), then sends;
  * recv() waits until a message has arrived, sleeps for the delay (delivery at the
    receiver), then returns it;
  * both write a line in the event log, through the `log` function it is given.

A message therefore needs the sender's delay plus the receiver's delay. Each end uses the
same delay for sending and for receiving, so the request (client send + server recv) and
the reply (server send + client recv) take the SAME total time.
"""
import random
import time


class Channel:
    """One end of the line between this MPI rank and its peer."""

    def __init__(self, comm, peer, min_delay, max_delay, log, seed=None):
        """
        comm       the MPI communicator (comm.send / comm.recv / comm.iprobe are used)
        peer       the rank at the other end of the line
        min_delay, max_delay
                   the delay of this end is drawn once, uniformly, between these two values
                   (seconds)
        log        function(text) that records an event in the event log
        seed       if given, the random generator is seeded with seed + rank BEFORE the delay
                   is drawn, so the same seed always gives the same delay; the rank is added
                   so the two ends do not get the same number
        """
        self.comm = comm
        self.peer = peer
        self.log = log
        if seed is not None:
            random.seed(seed + comm.Get_rank())           # set the seed first...
        self.delay = random.uniform(min_delay, max_delay)  # ...then draw the delay, once

    def send(self, obj, tag, what):
        """Send `obj` to the peer, after sleeping for the delay (the message is on the wire).

        `tag` tells the kinds of message apart; `what` is only the name shown in the log."""
        self.log(f"sends {what} (+{self.delay:.2f} s on the wire)")   # logged BEFORE the sleep: the send starts now
        time.sleep(self.delay)                            # simulated transmission time at the sender
        self.comm.send(obj, dest=self.peer, tag=tag)      # hand the message to MPI

    def recv(self, tag, what):
        """Wait for a message with `tag` from the peer, sleep for the delay, and return it."""
        # iprobe() only ASKS whether a matching message is waiting and returns at once, so the
        # loop looks again every 5 ms until the message has arrived.
        while not self.comm.iprobe(source=self.peer, tag=tag):
            time.sleep(0.005)
        time.sleep(self.delay)                            # simulated delivery time at the receiver
        obj = self.comm.recv(source=self.peer, tag=tag)   # the message is there: take it
        self.log(f"receives {what} (+{self.delay:.2f} s delivery)")   # logged AFTER the sleep: now it is delivered
        return obj
