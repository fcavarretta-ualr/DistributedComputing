"""
raft_test.py -- the leader election of Raft, run with MPI (mpi4py).

Each MPI rank is one server, and its rank is its ID: P0, P1, ..., P(n-1).
Every server starts as a FOLLOWER of a leader that is gone, so nobody sends heartbeats.
The first server whose RANDOM election timeout expires becomes a CANDIDATE: it starts a
new TERM, votes for itself and asks the others for their vote. A MAJORITY of votes makes
it the LEADER, and the leader sends HEARTBEATS to keep the others as followers.

Messages (each one is a Python tuple):
    ("REQUEST_VOTE", term, sender)    a candidate asks for a vote
    ("VOTE", term, granted)           the answer (granted is True or False)
    ("HEARTBEAT", term)               the leader says "I am alive"

Run (use at least 3 ranks; the output differs a little at every run):
    mpirun -n 5 python3 raft_test.py
Add --oversubscribe after mpirun if the machine has fewer cores than ranks, and
--allow-run-as-root if you run as root (e.g. in a container).
"""
import random                         # for the random election timeouts
import time                           # for the clock and for sleeping

from mpi4py import MPI                # MPI: how the processes (servers) exchange messages

comm = MPI.COMM_WORLD                 # the group of all the processes
n = comm.Get_size()                   # number of servers in the cluster
DURATION = 5.0                        # seconds before the demo ends
HEARTBEAT = 0.3                       # the leader's heartbeat period (seconds)
START = time.time()                   # when the program started, to print relative times


def say(me, text):
    # Print the time since the start, the server and what it does.
    print(f"[{time.time() - START:4.1f}s] P{me} {text}", flush=True)


def receive(wait=None):
    """Return the next message. With `wait`, give up after `wait` seconds and return None."""
    if wait is None:                                # no time limit?
        return comm.recv()                          # block until a message arrives
    end = time.time() + wait                        # the moment I stop waiting
    while time.time() < end:                        # until the time is over...
        if comm.iprobe():                           # is a message waiting?
            return comm.recv()                      # yes: read it and return it
        time.sleep(0.01)                            # no: sleep a little, then look again
    return None                                     # time is over: nothing arrived


def new_timeout():
    """A RANDOM election timeout: it is what makes split votes unlikely to repeat."""
    return random.uniform(1.0, 2.0)                 # a different value for every server and every time


def start_election(me, term):
    """Ask every other server for its vote in the new term: RequestVote."""
    say(me, f"times out: candidate in term {term}")             # tell what is happening
    for p in range(n):                                          # for every server...
        if p != me:                                             # ...but me (I already voted for myself)
            comm.send(("REQUEST_VOTE", term, me), dest=p)       # ask for its vote


def finish():
    """Wait for everybody, then throw away the messages nobody read (only to keep MPI quiet)."""
    comm.barrier()                    # wait until all the servers have reached this point
    while comm.iprobe():              # while unread messages are left...
        comm.recv()                   # ...read and discard them


def process():
    """The behaviour of ONE server. Every rank runs this function."""
    me = comm.Get_rank()              # my rank is my ID
    others = [p for p in range(n) if p != me]       # the IDs of all the other servers
    state = "follower"                # everybody starts as a follower
    term = 0                          # the current term (the "election number"), 0 at the start
    voted_for = None                  # the candidate I voted for in this term (one vote per term)
    votes = 0                         # the votes I have collected (only meaningful for a candidate)
    timeout = new_timeout()           # no heartbeat for this long -> become a candidate
    last_heard = time.time()          # the last time I heard from a leader (or voted)

    while time.time() - START < DURATION:           # run until the demo is over
        # The leader waits one heartbeat period; the others wait until their timeout expires.
        wait = HEARTBEAT if state == "leader" else max(0, last_heard + timeout - time.time())
        message = receive(wait)       # wait for a message, but not longer than `wait`

        if message is None:           # nothing arrived: a timer expired
            if state == "leader":     # the leader's heartbeat period is over
                for p in others:                            # to every other server...
                    comm.send(("HEARTBEAT", term), dest=p)  # ...say "I am alive"
            else:                     # no heartbeat for the whole timeout
                state = "candidate"                         # I become a candidate...
                term = term + 1                             # ...in a new term...
                voted_for = me                              # ...and I vote for myself
                votes = 1                                   # that is my first vote
                timeout = new_timeout()                     # a new random timeout, in case of a split vote
                last_heard = time.time()                    # restart the timeout from now
                start_election(me, term)                    # ask the others for their votes
            continue                  # go back and wait for the next message

        # A higher term means my information is old: I go back to being a follower.
        if message[1] > term:         # every message carries the term of its sender
            if state != "follower":   # I was a candidate or a leader of an old term
                say(me, f"sees term {message[1]}: follower")    # tell what is happening
            state = "follower"        # I step down
            term = message[1]         # I adopt the newer term
            voted_for = None          # I have not voted yet in the new term

        if message[0] == "REQUEST_VOTE":                # a candidate asks for my vote
            # One vote per term: the first candidate that asks gets it.
            candidate = message[2]    # who is asking
            grant = message[1] == term and voted_for in (None, candidate)   # same term, and I have not voted for another
            if grant:                 # I give my vote
                voted_for = candidate                   # remember that I voted in this term
                last_heard = time.time()                # a vote also postpones my own timeout
                say(me, f"votes for P{candidate} in term {term}")           # tell what is happening
            comm.send(("VOTE", term, grant), dest=candidate)                # answer yes or no

        elif message[0] == "VOTE":                      # somebody answers my request
            if state == "candidate" and message[1] == term and message[2]:  # I am a candidate, same term, vote granted
                votes += 1            # one more vote
                if votes > n / 2:     # a majority: more than half of the servers
                    state = "leader"  # I win the election
                    say(me, f"gets {votes} of {n} votes: leader of term {term}")    # tell what is happening

        elif message[0] == "HEARTBEAT":                 # the leader says "I am alive"
            # A valid leader exists: stay (or become) a follower and wait again.
            if message[1] == term:    # the heartbeat belongs to my current term
                state = "follower"    # a candidate gives up: someone else won
                last_heard = time.time()                # restart the timeout from now
                timeout = new_timeout()                 # draw a new random timeout

        else:                         # none of the known messages
            say(me, "Unknown message")


if __name__ == "__main__":            # only when the file is run, not when it is imported
    process()                         # run the behaviour of this server
    finish()                          # then wait for everybody and clean up
