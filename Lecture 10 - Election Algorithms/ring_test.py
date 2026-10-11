"""
ring_test.py -- the ring election algorithm, run with MPI (mpi4py).

Each MPI rank runs the function process(), and its rank is its ID: P0, P1, ..., P(n-1).
The processes form a logical ring (P0 -> P1 -> ... -> P(n-1) -> P0): each process knows
its successor and sends messages only to it. There is no token.
The old coordinator, the highest rank, has crashed and P1 is the first to notice it.

Messages (each one is a Python tuple):
    ("ELECTION", ids)          the IDs collected so far along the ring
    ("COORDINATOR", winner)    the winner, announced once around the ring

Run (use at least 3 ranks):
    mpirun -n 5 python3 ring_test.py
Add --oversubscribe after mpirun if the machine has fewer cores than ranks, and
--allow-run-as-root if you run as root (e.g. in a container).
"""
import time

from mpi4py import MPI

comm = MPI.COMM_WORLD
n = comm.Get_size()
CRASHED = n - 1                       # the old coordinator: it never answers
START = time.time()


def say(me, text):
    print(f"[{time.time() - START:4.1f}s] P{me} {text}", flush=True)


def receive(wait=None):
    """Return the next message. With `wait`, give up after `wait` seconds and return None."""
    if wait is None:
        return comm.recv()                          # block until a message arrives
    end = time.time() + wait
    while time.time() < end:
        if comm.iprobe():                           # is a message waiting?
            return comm.recv()
        time.sleep(0.01)
    return None


def successor(me):
    """The next process in the ring, skipping the crashed one.
    (A real process would find out by timing out and then trying the next one.)"""
    nxt = (me + 1) % n
    return (nxt + 1) % n if nxt == CRASHED else nxt


def start_election(me):
    """Send an ELECTION message with my own ID to my successor."""
    say(me, "starts an election: sends its ID to its successor")
    comm.send(("ELECTION", [me]), dest=successor(me))


def finish():
    """Wait for everybody, then throw away the messages nobody read (only to keep MPI quiet)."""
    comm.barrier()
    while comm.iprobe():
        comm.recv()


def process():
    """The behaviour of ONE process. Every rank runs this function."""
    me = comm.Get_rank()              # my rank is my ID
    if me == CRASHED:
        time.sleep(3)                 # a crashed process is silent
        return

    initiator = me == 1               # P1 is the one that notices the crash
    if initiator:
        start_election(me)

    while True:
        message = receive()           # wait for the next message from the predecessor

        if message[0] == "ELECTION":
            ids = message[1]
            if me in ids:
                # The message went around the whole ring: it holds every alive ID.
                winner = max(ids)
                say(me, f"gets the list {ids} back: the winner is P{winner}")
                comm.send(("COORDINATOR", winner), dest=successor(me))
            else:
                # Add my ID and pass the message on.
                say(me, f"adds its ID to the list {ids}")
                comm.send(("ELECTION", ids + [me]), dest=successor(me))

        elif message[0] == "COORDINATOR":
            winner = message[1]
            say(me, f"accepts P{winner} as the coordinator")
            if not initiator:                     # the initiator stops the message: it went around
                comm.send(message, dest=successor(me))
            break

        else:
            say(me, "Unknown message")


if __name__ == "__main__":
    process()
    finish()
