"""
vector_test_2.py -- vector clock, CASE 2 of the slide, run with MPI (mpi4py).

Three MPI ranks are the three processes (rank 0 = P1, rank 1 = P2, rank 2 = P3).
They exchange messages with comm.send() / comm.recv() and keep their clocks with the
VectorClock class of vector_clock.py.

Message pattern of Case 2 (sender -> receiver):
    m1: P2 -> P1     m3: P1 -> P2     m4: P2 -> P3     m2: P1 -> P3
    P1:  receive m1, send m3, local event, send m2   (m2 now leaves LAST)
    P2:  send m1, receive m3, send m4
    P3:  receive m4, receive m2          (m4 now arrives FIRST)

HOW THE RANKS TALK  (mpi4py)
----------------------------
* mpirun starts the SAME program once per rank; comm.Get_rank() tells each copy who
  it is, and each copy runs only its own procedure (p1, p2 or p3).
* comm.send(obj, dest, tag) sends a Python object (here the whole vector);
  comm.recv(source, tag) blocks until a message with that source and tag arrives.
  The tag is the message number (m3 -> 3), so MPI matches "m3" with "m3".
* comm.gather() collects every rank's list of events on rank 0, which prints them
  in one global order.

HOW THE EVENTS ARE ORDERED
--------------------------
Every event is stamped with a vector. Sorting the events by the SUM of the entries
of their vector puts every cause before its effect: if a happened-before b, then
V(a) <= V(b) entry by entry and V(a) != V(b), so sum(V(a)) < sum(V(b)). Events with
the same sum are concurrent, so their relative order is arbitrary; we list the
higher process number first, just to make the output reproducible.

Run (exactly 3 ranks):
    mpirun -n 3 python3 vector_test_2.py
Add --oversubscribe after mpirun if the machine has fewer than 3 cores.
"""
from mpi4py import MPI

from vector_clock import VectorClock

# The vectors written on the slide, in the order each process computes them.
EXPECTED = {
    "P1": [[1, 1, 0], [2, 1, 0], [3, 1, 0], [4, 1, 0]],
    "P2": [[0, 1, 0], [2, 2, 0], [2, 3, 0]],
    "P3": [[2, 3, 1], [4, 3, 2]],
}

P1, P2, P3 = 0, 1, 2                  # ranks


def p1(comm):
    """P1 (index 0): receives m1, sends m3, has a local event, sends m2."""
    clock = VectorClock(0, 3)           # P1 owns entry 0 of the vector; starts at [0, 0, 0]
    events = []                         # (description, vector), in the order they happen

    ts = comm.recv(source=P2, tag=1)    # blocks until P2 has sent m1; ts = [0, 1, 0]
    counter = clock.receive(ts)         # max([0,0,0],[0,1,0]) = [0,1,0], then own entry +1 -> [1,1,0]
    events.append((f"P1 receives m1 {ts}", counter))

    counter = clock.tick()              # send m3 (first send in Case 2): own entry +1 -> [2,1,0]
    comm.send(counter, dest=P2, tag=3)  # ship a copy of the whole vector as ts(m3)
    events.append(("P1 sends m3 to P2", counter))

    counter = clock.tick()              # local event (the grey square on the slide): [3,1,0]
    events.append(("P1 local event", counter))

    counter = clock.tick()              # send m2 (last send in Case 2): [4,1,0]
    comm.send(counter, dest=P3, tag=2)  # ts(m2) = [4,1,0]
    events.append(("P1 sends m2 to P3", counter))
    return events


def p2(comm):
    """P2 (index 1): sends m1 to P1, receives m3, sends m4 to P3."""
    clock = VectorClock(1, 3)           # P2 owns entry 1 of the vector; starts at [0, 0, 0]
    events = []

    counter = clock.tick()              # send m1: own entry +1 -> [0,1,0]
    comm.send(counter, dest=P1, tag=1)  # ts(m1) = [0,1,0]
    events.append(("P2 sends m1 to P1", counter))

    ts = comm.recv(source=P1, tag=3)    # ts = [2,1,0]
    counter = clock.receive(ts)         # max([0,1,0],[2,1,0]) = [2,1,0], then +1 -> [2,2,0]
    events.append((f"P2 receives m3 {ts}", counter))

    counter = clock.tick()              # send m4: [2,3,0]
    comm.send(counter, dest=P3, tag=4)  # ts(m4) = [2,3,0]
    events.append(("P2 sends m4 to P3", counter))
    return events


def p3(comm):
    """P3 (index 2): receives m4, then m2. Never sends."""
    clock = VectorClock(2, 3)           # P3 owns entry 2 of the vector; starts at [0, 0, 0]
    events = []

    ts = comm.recv(source=P2, tag=4)    # ts = [2,3,0]
    counter = clock.receive(ts)         # max([0,0,0],[2,3,0]) = [2,3,0], then +1 -> [2,3,1]
    events.append((f"P3 receives m4 {ts}", counter))

    ts = comm.recv(source=P1, tag=2)    # ts = [4,1,0]
    counter = clock.receive(ts)         # max([2,3,1],[4,1,0]) = [4,3,1], then +1 -> [4,3,2]
    events.append((f"P3 receives m2 {ts}", counter))
    return events


if __name__ == "__main__":
    comm = MPI.COMM_WORLD

    if comm.Get_size() != 3:
        raise SystemExit("needs exactly 3 ranks: mpirun -n 3 python3 vector_test_2.py")

    # Every rank runs only its own procedure; rank 0 receives the three event lists.
    events = (p1, p2, p3)[comm.Get_rank()](comm)
    reports = comm.gather(events, root=0)

    if comm.Get_rank() == 0:
        for name, evs in zip(("P1", "P2", "P3"), reports):
            assert [counter for _, counter in evs] == EXPECTED[name], f"{name} differs from the slide"

        # Sort by (sum of the vector, -process number): see the docstring.
        all_events = [e for evs in reports for e in evs]
        all_events.sort(key=lambda e: (sum(e[1]), -int(e[0][1])))

        print("Vector clock, case 2 -- events in order")
        for step, (text, counter) in enumerate(all_events, start=1):
            print(f"{step:>2}. {text:<28} -> {counter}")
