"""
ntp_test.py -- a client and a server with their own clocks, run with MPI (mpi4py).

Two MPI ranks: rank 0 is the SERVER (its clock is the reference), rank 1 is the CLIENT
(its clock is wrong). Each one has TWO threads:

    clock thread  (background)  sleeps, then ticks its clock, forever -- see ntp_clock.py
    main thread                 runs the NTP protocol and reads the clock when it needs it

                    sleep per tick   tick_increment   clock starts at
    server (rank 0)       2 s              2               1000
    client (rank 1)       1 s              1               1000 - difference (960 by default)

Both clocks advance one unit per real second, but the server's clock jumps by 2 every 2
seconds and the client's by 1 every second.

WHAT HAPPENS
------------
1. Both clock threads start ticking in the background.
2. After the client's 5th tick (it sleeps 5.5 seconds) it reads T0C and sends a request.
3. The server waits for the request, reads T1S, spends a random time processing the request,
   reads T2S and replies with T1S and T2S.
4. The client receives the reply, reads T3C and estimates theta and delta
   (ntp_clock.estimate).
5. The client REALIGNS: its clock thread adds theta/5 to the clock at each of the next 5
   ticks, on top of the usual tick_increment, instead of jumping (a clock that jumped could
   run backward or repeat a time; see the "Avoiding Backward Clock Adjustment" slide). For a
   negative theta (client ahead) the clock stands still for some ticks instead of running
   backward.
6. The client simply waits until its clock thread has finished realigning, the server waits
   a while longer, and both stop their clocks and end.

SEND AND RECV
-------------
The client and the server only call channel.send(...) and channel.recv(...). The Channel
class (ntp_channel.py) does everything else: it draws ONE random delay between MIN_DELAY and
MAX_DELAY when it is created (after the seed is set), and uses it on every call.

    channel.send(...)   sleeps for the delay (the message is "on the wire"), then sends it
    channel.recv(...)   waits until the message is there, sleeps for the delay (delivery at
                        the receiver), then returns it

A message therefore needs the sender's delay plus the receiver's delay. Because each process
uses the same delay for sending and for receiving, the request (client send + server recv)
and the reply (server send + client recv) take the SAME total time, so the asymmetry that
normally spoils the estimate of theta is absent here; what is left is the error of the
coarse ticks. The server also sleeps a random time between T1S and T2S, which simulates the
processing of the request. Use --seed to repeat a run.

THE OUTPUT
----------
Every event is printed THE MOMENT IT HAPPENS, by the process it happens in, with the real
time since the start and that process's own clock: you can watch the run as it goes (each
print is flushed, so nothing waits in a buffer). At the end rank 0 prints the same events
again in time order, with BOTH clocks on every line (the server's and the client's) and their
difference (server - client), so you can see the client's clock catch up, followed by the four timestamps,
delta and theta. (The two values on a line of that table are not read at the same instant
by a common observer: each is the last value its own process reported.)

Run (exactly 2 ranks):
    mpirun -n 2 python3 ntp_test.py                      (client 40 behind)
    mpirun -n 2 python3 ntp_test.py --difference 25      (client 25 behind)
    mpirun -n 2 python3 ntp_test.py --difference -10     (client 10 ahead)
    mpirun -n 2 python3 ntp_test.py --seed 1             (same random delays every time)
Add --oversubscribe after mpirun if the machine has fewer than 2 cores.
"""
import argparse                       # reads the command-line options (--difference, --seed)
import random                         # the random delay and the random processing time
import time                           # time.sleep() and the real-time stamps of the events

from mpi4py import MPI                # MPI: the two processes and the messages between them

from ntp_channel import Channel               # send() and recv() with the simulated delay
from ntp_clock import TickClock, estimate     # the clock class and the theta/delta formulas

SERVER, CLIENT = 0, 1                 # MPI ranks: rank 0 is the server, rank 1 is the client
SERVER_START = 1000                   # what the server's clock shows at the start
REQUEST, REPLY = 1, 2                 # message tags: they tell the two kinds of message apart

WARMUP_TICKS = 5                      # client ticks (= seconds) before it sends the request
REALIGN_TICKS = 5                     # ticks over which the client corrects its clock
MIN_DELAY, MAX_DELAY = 0.1, 0.8       # the one random delay of the Channel is drawn from here
MIN_PROCESSING, MAX_PROCESSING = 0.2, 1.0   # random time the server takes to process a request
SERVER_WAIT = 30                      # how long the server keeps running after its reply, in seconds

# The state of THIS process. Each MPI rank is a separate process with its own copy of these
# variables, so the server and the client do not share them.
role = ""                             # "server" or "client": names the process in the event log
clock = None                          # this process's TickClock, created in server() / client()
events = []                           # the event log: (real time, role, description, clock value)
start = 0.0                           # real time at which the run started


def log(text, value=None):
    """Record an event and print it at once: real time since the start, who, what, clock value.

    The clock value is read now, unless the caller already has it (the clock thread passes
    the value it has just produced, so the log shows exactly that tick)."""
    now = time.monotonic() - start                    # real seconds since the run started
    value = clock.read() if value is None else value
    events.append((now, role, text, value))           # kept for the table printed at the end
    # Print immediately. flush=True pushes the line out now: without it Python would hold it
    # in a buffer (when the output is not a terminal) and we would see nothing until the end.
    print(f"{now:5.1f} s  {role:<6}  {text:<46} clock = {value:.1f}", flush=True)


def server(channel):
    """The server: wait for the request, process it, reply with the two server timestamps."""
    global role, clock                                # we set the module-level variables
    role = "server"                                   # the event log will show "server"

    # The server's clock. The parameters of TickClock (see ntp_clock.py):
    #   start=SERVER_START   the value the clock shows at the beginning: 1000. The server is the
    #                        reference, so this is the "true" time the client has to reach.
    #   tick_increment=2     how much the counter grows at EACH tick: +2. It is the resolution of
    #                        the clock: it shows 1000, 1002, 1004, ... and never an odd value.
    #   period=2             real seconds between two ticks, i.e. the sleep of the clock thread:
    #                        2 s. Speed = tick_increment / period = 2 / 2 = 1 unit per second.
    #   on_tick=...          function called with the new value right after every tick; here
    #                        it records "tick" in the event log (the printed table).
    clock = TickClock(start=SERVER_START, tick_increment=2, period=2,
                      on_tick=lambda value: log("tick", value))
    clock.start()                                     # the clock now runs in the background

    channel.recv(REQUEST, "request")                  # wait until the client's request arrives
    t1s = clock.read()                                # T1S: server clock when the request is received

    # Simulate the time the server needs to handle the request: a random time between
    # T1S and T2S. The clock thread keeps ticking while the main thread sleeps.
    processing = random.uniform(MIN_PROCESSING, MAX_PROCESSING)
    log(f"processes the request (takes {processing:.2f} s)")
    time.sleep(processing)

    t2s = clock.read()                                # T2S: server clock when the reply is sent
    channel.send((t1s, t2s), REPLY, "reply")          # share both timestamps with the client

    # There is nothing more to do, but the clock keeps ticking in the background: wait long
    # enough for the client to finish realigning, so the log shows both clocks until the end.
    time.sleep(SERVER_WAIT)
    clock.stop()                                      # stop the clock thread
    return {}                                         # the server has no results to report


def client(channel, difference):
    """The client: send the request, receive the reply, estimate theta and delta, realign."""
    global role, clock                                # we set the module-level variables
    role = "client"                                   # the event log will show "client"

    # The client's clock. The parameters of TickClock (see ntp_clock.py):
    #   start=SERVER_START - difference
    #                        the value the clock shows at the beginning: 1000 - difference, so 960
    #                        by default. This is the error the protocol will have to find and
    #                        remove: the client starts `difference` behind the server.
    #   tick_increment=1     how much the counter grows at EACH tick: +1 (finer than the server's
    #                        +2): it shows 960, 961, 962, ...
    #   period=1             real seconds between two ticks, i.e. the sleep of the clock thread:
    #                        1 s. Speed = tick_increment / period = 1 / 1 = 1 unit per second,
    #                        the same as the server's, so the difference does not change by itself.
    #   on_tick=...          function called with the new value right after every tick; here
    #                        it records "tick" in the event log (the printed table).
    clock = TickClock(start=SERVER_START - difference, tick_increment=1, period=1,
                      on_tick=lambda value: log("tick", value))
    clock.start()                                     # the clock now runs in the background

    # Let the clock tick 5 times: 5 ticks of 1 s, plus half a second of margin so the sleep
    # does not end at the very instant of the 5th tick.
    time.sleep(WARMUP_TICKS + 0.5)
    t0c = clock.read()                                # T0C: client clock when the request is sent
    channel.send(None, REQUEST, "request")            # the request carries no data: it is just "what time is it?"

    t1s, t2s = channel.recv(REPLY, "reply")           # the reply carries the server's T1S and T2S
    t3c = clock.read()                                # T3C: client clock when the reply is received
    theta, delta = estimate(t0c, t1s, t2s, t3c)       # the formulas of the slides (ntp_clock.py)

    # Realign: the clock thread adds theta / REALIGN_TICKS to the clock at each of the next
    # REALIGN_TICKS ticks, instead of the main thread setting the clock to a new value.
    log(f"realigns by {theta:+.1f} over {REALIGN_TICKS} ticks")
    clock.realign(theta, REALIGN_TICKS)

    # Just wait for the clock thread to finish: realigning takes REALIGN_TICKS ticks of 1 s
    # (a clock that is ahead must stand still and needs about |theta| ticks), plus one second
    # of margin.
    time.sleep(max(REALIGN_TICKS, -theta) * 2 + 1)
    clock.stop()                                      # stop the clock thread
    return {"T0C": t0c, "T1S": t1s, "T2S": t2s, "T3C": t3c, "theta": theta, "delta": delta}


if __name__ == "__main__":
    # ---- command line ----------------------------------------------------------------------
    parser = argparse.ArgumentParser(description="NTP example: one server, one client.")
    parser.add_argument("--difference", type=float, default=40,
                        help="server clock minus client clock at the start (default 40: client behind)")
    parser.add_argument("--seed", type=int, help="seed of the random numbers (repeats a run)")
    args = parser.parse_args()

    # ---- MPI setup -------------------------------------------------------------------------
    comm = MPI.COMM_WORLD                             # the group of all the ranks started by mpirun
    rank = comm.Get_rank()                            # this process's number: 0 = server, 1 = client

    if comm.Get_size() != 2:                          # exactly one server and one client
        raise SystemExit("needs exactly 2 ranks: mpirun -n 2 python3 ntp_test.py")

    if rank == 0:                                     # one header line, printed before anything happens
        print(f"NTP -- server (sleep 2 s, tick 2) and client (sleep 1 s, tick 1), "
              f"clock difference {args.difference:g}", flush=True)

    # ---- the channel: it sets the seed, then draws its one random delay -------------------------
    channel = Channel(comm, peer=1 - rank, min_delay=MIN_DELAY, max_delay=MAX_DELAY,
                      log=log, seed=args.seed)

    comm.Barrier()                                    # wait until both ranks are here...
    start = time.monotonic()                          # ...so both start counting real time together

    # ---- run: each rank executes only its own role -----------------------------------------
    result = server(channel) if rank == SERVER else client(channel, args.difference)

    # Collect the event log and the result of every rank on rank 0 (it returns a list indexed by rank).
    reports = comm.gather((events, result), root=0)

    # ---- print: only rank 0 -----------------------------------------------------------------
    if rank == 0:
        (server_events, _), (client_events, r) = reports

        # The estimate must follow the formulas of the slides, from the four timestamps.
        assert r["delta"] == ((r["T3C"] - r["T0C"]) - (r["T2S"] - r["T1S"])) / 2
        assert r["theta"] == ((r["T1S"] - r["T0C"]) + (r["T2S"] - r["T3C"])) / 2

        # The live lines above show only the clock of the process that printed them. Here the
        # same events are replayed in time order, keeping the latest clock value of each side,
        # so both clocks can be compared on one line, with their difference (server - client):
        # it starts at `difference` and shrinks towards 0 while the client realigns.
        shown = {"server": SERVER_START, "client": SERVER_START - args.difference}
        print("\nAll events in time order, with both clocks:")
        print(f"{'':>7}  {'':<6}  {'':<46} {'server':>8} {'client':>8} {'server-client':>14}")
        client_end = max(e[0] for e in client_events)  # after this the client reports nothing more
        for t, who, text, value in sorted(server_events + client_events):   # sorted by real time
            if t > client_end:                        # the client's value would be stale: stop here
                break
            shown[who] = value                        # this event updates the clock of its own side
            gap = shown["server"] - shown["client"]   # how far the client is behind the server
            print(f"{t:5.1f} s  {who:<6}  {text:<46} {shown['server']:>8.1f} {shown['client']:>8.1f} {gap:>14.1f}")
        print()
        print(f"T0C = {r['T0C']:g}  T1S = {r['T1S']:g}  T2S = {r['T2S']:g}  T3C = {r['T3C']:g}")
        print(f"delta = {r['delta']:g}    theta = {r['theta']:+g}")
