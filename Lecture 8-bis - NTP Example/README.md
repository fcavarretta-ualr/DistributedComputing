# NTP Example

A client and a server, each with its own clock running as a background thread (sleep, then
tick). After 5 ticks (it sleeps 5.5 s) the client asks the server for its timestamps, estimates the round-trip
delay (delta) and the time difference (theta), and realigns its clock over 5 ticks.

## Files

| File | What it is |
|------|------------|
| `ntp_clock.py` | `TickClock` (a counter that a background thread increments by `tick_increment` at every tick, and that can realign itself gradually) and `estimate()`, which computes theta and delta from T0C, T1S, T2S, T3C. |
| `ntp_channel.py` | The `Channel` class: one end of the line between client and server. `send()` and `recv()` handle the waiting, the simulated delay and the log. |
| `ntp_test.py` | The server (rank 0) and the client (rank 1), exchanging messages with MPI. |

## Requirements

* Python 3.8 or later
* An MPI implementation (Open MPI or MPICH) and `pip install mpi4py`

## How to run

```
mpirun -n 2 python3 ntp_test.py                      # client 40 behind the server (default)
mpirun -n 2 python3 ntp_test.py --difference 25      # client 25 behind
mpirun -n 2 python3 ntp_test.py --difference -10     # client 10 ahead
mpirun -n 2 python3 ntp_test.py --seed 1             # same random transmission times every run
```

`--difference D` is the server's clock minus the client's clock at the start. If the client is
ahead (negative D) its clock cannot run backward, so it stands still for some ticks while it
absorbs the correction, which takes longer than 5 ticks (about 11 ticks for the example above).

Add `--oversubscribe` after `mpirun` if the machine has fewer than 2 cores
(and `--allow-run-as-root` if you run as root, e.g. in a container).

## What the two programs do

Each program has two threads: a **clock thread** in the background (sleep, then tick) and
the **main thread** that runs the protocol and reads the clock when it needs the time.

| | sleep per tick | `tick_increment` | clock starts at |
|---|---|---|---|
| server | 2 s | 2 | 1000 |
| client | 1 s | 1 | 1000 - difference (960 by default) |

Both clocks advance one unit per real second. After the client's 5th tick it reads T0C and
sends the request. The server reads T1S and T2S and replies with both. The client reads T3C,
estimates theta and delta, and asks its clock thread to add theta/5 at each of the next 5
ticks on top of the usual tick_increment (no jump, so the clock never runs backward).

The client and the server only call `channel.send(...)` and `channel.recv(...)`; the `Channel`
class does the rest. It draws ONE random delay (0.1 s to 0.8 s) when it is created, after the
seed is set, and uses that same delay on every call: `send()` sleeps for it (the message is on
the wire) and then sends; `recv()` waits until the message is there, sleeps for it (delivery at
the receiver) and then returns it. Each end uses the same delay for sending and receiving, so
the request and the reply take the same total time and theta is limited only by the coarse
ticks of the clocks (delta can come out slightly negative, because the server's clock moves in
steps of 2). The server also sleeps a random time (0.2 s to 1.0 s) between reading T1S and T2S,
which simulates the processing of the request. `--seed` makes the random numbers repeat.

There is no "finished" message: after starting the realignment the client just waits for its
clock thread to finish, and the server just keeps its clock running for 15 more seconds
(`SERVER_WAIT`) before it stops. A run takes about 25 seconds.

## Output

Every event is printed **the moment it happens**, by the process it happens in, with the real
time since the start and that process's own clock (each print is flushed, so you can watch
the run as it goes). At the end rank 0 prints the same events again in time order with both
clocks on every line (the server's and the client's) and their difference (server - client), so you
can see the client catch up, then
the four timestamps, delta and theta. The random numbers (and so delta and theta) change from
run to run unless you give a `--seed`. To change the scenario, edit the constants at the top of
`ntp_test.py` and the starting values in `server()` / `client()`.

## The formulas

```
delta = ((T3C - T0C) - (T2S - T1S)) / 2
theta = ((T1S - T0C) + (T2S - T3C)) / 2
```

theta is the server's clock minus the client's clock: positive when the client is behind
and has to move forward. The estimate is exact when the request and reply delays are equal.
