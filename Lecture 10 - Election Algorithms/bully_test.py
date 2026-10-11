"""
bully_test.py -- the bully election algorithm, run with MPI (mpi4py).

Each MPI rank is one process, and its rank is its ID: P0, P1, ..., P(n-1).
The coordinator is the alive process with the HIGHEST ID. Here the old coordinator,
the highest rank, has crashed, and P1 is the first to notice it.

Messages (each one is a Python tuple):
    ("ELECTION", sender)       "is anybody alive with a higher ID than mine?"
    ("OK", sender)             "I am alive and my ID is higher: I take over."
    ("COORDINATOR", winner)    "I won the election: I am the new coordinator."

Run (use at least 3 ranks):
    mpirun -n 5 python3 bully_test.py
Add --oversubscribe after mpirun if the machine has fewer cores than ranks, and
--allow-run-as-root if you run as root (e.g. in a container).
"""
import sys
import time

from mpi4py import MPI

comm = MPI.COMM_WORLD
n = comm.Get_size()
CRASHED = n - 1                       # the old coordinator: it never answers
TIMEOUT = 1.0                         # seconds of silence before deciding "nobody answered"
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


def start_election(me):
    """Ask every higher process: ELECTION."""
    say(me, "starts an election")
    for p in range(me + 1, n):
        comm.send(("ELECTION", me), dest=p)         # sending to a crashed process is harmless


def finish():
    """Wait for everybody, then throw away the messages nobody read (only to keep MPI quiet)."""
    comm.barrier()
    while comm.iprobe():
        comm.recv()


def process():
    """The behaviour of ONE process. Every rank runs this function."""
    me = comm.Get_rank()              # my rank is my ID
    if me == CRASHED:
        # A crashed process is silent: it reads nothing and answers nothing.
        finish()
        sys.exit()

    initiator = me == 1               # P1 is the one that notices the crash
    if initiator:
        start_election(me)

    while True:
        message = receive(TIMEOUT)    # wait for the next message

        if message is None:
            # Nobody answered ELECTION: nobody higher is alive, so I win.
            if initiator:
                say(me, "gets no answer: it wins and announces itself")
                for p in range(n):
                    if p != me:
                        comm.send(("COORDINATOR", me), dest=p)
                say(me, "is the coordinator")
                break
            continue

        if message[0] == "ELECTION":
            # A lower process is asking: I am higher, so I answer OK and take over the election.
            sender = message[1]
            say(me, f"answers OK to P{sender}")
            comm.send(("OK", me), dest=sender)
            if not initiator:
                initiator = True
                start_election(me)

        elif message[0] == "OK":
            # Somebody higher is alive: I give up and wait for its COORDINATOR message.
            initiator = False

        elif message[0] == "COORDINATOR":
            winner = message[1]
            say(me, f"accepts P{winner} as the coordinator")
            break

        else:
            say(me, "Unknown message")


if __name__ == "__main__":
    process()
    finish()
