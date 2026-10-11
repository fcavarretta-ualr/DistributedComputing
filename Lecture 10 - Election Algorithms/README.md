# Lecture 10 - Election Algorithms

Minimal Python examples of the three election algorithms of the lecture. Each process is an
MPI rank (rank = process ID: P0, P1, ...) that runs the function `process()`, which holds the
whole behaviour of one process, and the messages (Python tuples) are sent with `mpi4py`. In the
bully and ring examples the old coordinator (the highest rank) has crashed and P1 is the first
process to notice it. In the Raft example the old leader is gone and nobody sends heartbeats.

## Files

| File | What it is |
|------|------------|
| `bully_test.py` | Bully algorithm: ELECTION, OK and COORDINATOR messages; the highest alive ID wins. |
| `ring_test.py` | Ring algorithm: an ELECTION message collects the IDs along the logical ring, then a COORDINATOR message goes once around the ring. |
| `raft_test.py` | Raft leader election: random election timeouts, terms, RequestVote, majority vote, heartbeats. The output differs a little at every run. |

## Requirements

* Python 3.8 or later
* An MPI implementation (Open MPI or MPICH), e.g. `sudo apt install openmpi-bin`
* mpi4py: `pip install mpi4py`

## How to run

Use at least 3 ranks (5 is a good number):

```
mpirun -n 5 python3 bully_test.py
mpirun -n 5 python3 ring_test.py
mpirun -n 5 python3 raft_test.py
```

If the machine has fewer cores than ranks, add `--oversubscribe` after `mpirun`.
If you run as root (e.g. in a container), add `--allow-run-as-root`.

## Output

Every line starts with the time in seconds, then the process and what it does, e.g. for the
bully algorithm with 5 ranks (P4 crashed):

```
[ 0.0s] P1 starts an election
[ 0.0s] P2 answers OK to P1
...
[ 1.0s] P3 is the coordinator
[ 1.1s] P0 accepts P3 as the coordinator
```
