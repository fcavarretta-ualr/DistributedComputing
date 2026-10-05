"""
lamport_test.py -- the Lamport clock example of the "Lamport's Clock: Example" slide,
run with MPI (mpi4py).

Three MPI ranks are the three processes (rank 0 = P1, rank 1 = P2, rank 2 = P3). Each
rank owns one LamportClock (see lamport_clock.py); they share no memory and no clock,
and information moves only through messages.

Message pattern (sender -> receiver), as in the "Lamport's Clock: Example" slide:
    m1: P2 -> P1     m2: P1 -> P3
    P1:  receive m1, send m2, local event
    P2:  send m1
    P3:  receive m2, local event

HOW THE RANKS TALK  (mpi4py)
----------------------------
* mpirun starts the SAME program once per rank; comm.Get_rank() tells each copy who
  it is, and each copy runs only its own procedure (p1, p2 or p3).
* comm.send(obj, dest, tag) sends a Python object; comm.recv(source, tag) blocks until
  a message with that source and tag arrives. The tag is the message number (m3 -> 3),
  so MPI matches "m3" with "m3".
* comm.gather() collects every rank's list of events on rank 0, which prints them in
  one global order.

HOW THE EVENTS ARE SHOWN IN ORDER
---------------------------------
Each procedure records its events as (description, counter). Rank 0 sorts all events
by (counter, process number). Lamport's guarantee, a -> b implies C(a) < C(b), means
every cause comes before its effect in this order. Events with equal counters are
concurrent, so their order is arbitrary; breaking the tie by process number is exactly
the rule of Lamport's paper.

Run (exactly 3 ranks):
    mpirun -n 3 python3 lamport_test.py
Add --oversubscribe after mpirun if the machine has fewer than 3 cores.
"""
from mpi4py import MPI

from lamport_clock import LamportClock

# Counters each process must compute, in the order it computes them.
EXPECTED = {"P1": [2, 3, 4], "P2": [1], "P3": [4, 5]}

P1, P2, P3 = 0, 1, 2                  # ranks


def p1(comm):
    """P1: receives m1, sends m2, has a local event."""
    clock = LamportClock()
    events = []

    ts = comm.recv(source=P2, tag=1)    # blocks until P2 has sent m1; ts = 1
    counter = clock.receive(ts)         # max(0,1) = 1, then +1 -> 2
    events.append((f"P1 receives m1 (ts={ts})", counter))

    counter = clock.tick()              # send m2: 3
    comm.send(counter, dest=P3, tag=2)  # ts(m2) = 3
    events.append(("P1 sends m2 to P3", counter))

    counter = clock.tick()              # local event (the grey square on the slide): 4
    events.append(("P1 local event", counter))
    return events


def p2(comm):
    """P2: sends m1."""
    clock = LamportClock()
    events = []

    counter = clock.tick()              # send m1: 1
    comm.send(counter, dest=P1, tag=1)  # ts(m1) = 1
    events.append(("P2 sends m1 to P1", counter))
    return events


def p3(comm):
    """P3: receives m2, then has a local event."""
    clock = LamportClock()
    events = []

    ts = comm.recv(source=P1, tag=2)    # blocks until P1 has sent m2; ts = 3
    counter = clock.receive(ts)         # max(0,3) = 3, then +1 -> 4
    events.append((f"P3 receives m2 (ts={ts})", counter))

    counter = clock.tick()              # local event (the grey square on the slide): 5
    events.append(("P3 local event", counter))
    return events


if __name__ == "__main__":
    comm = MPI.COMM_WORLD

    if comm.Get_size() != 3:
        raise SystemExit("needs exactly 3 ranks: mpirun -n 3 python3 lamport_test.py")

    # Every rank runs only its own procedure; rank 0 receives the three event lists.
    events = (p1, p2, p3)[comm.Get_rank()](comm)
    reports = comm.gather(events, root=0)

    if comm.Get_rank() == 0:
        for name, evs in zip(("P1", "P2", "P3"), reports):
            assert [counter for _, counter in evs] == EXPECTED[name], f"{name} differs from the slide"

        all_events = [e for evs in reports for e in evs]
        all_events.sort(key=lambda e: (e[1], e[0][1]))  # (counter, process number)

        # Replay the events in that order and keep ONE list with the latest counter of every
        # process: counters[0] is C of P1, counters[1] is C of P2, counters[2] is C of P3.
        # No process owns this list (each only knows its own counter); it is the observer's
        # view of all the counters right after each event.
        counters = [0, 0, 0]
        print("Lamport clock -- events in order")
        for step, (text, counter) in enumerate(all_events, start=1):
            counters[int(text[1]) - 1] = counter          # text[1] is the process number
            print(f"{step:>2}. {text:<28} -> C = {counters}")
