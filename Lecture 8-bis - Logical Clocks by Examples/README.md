# Lecture 8-bis - Logical Clocks by Examples

Python examples for the Lamport and vector clock slides. Three processes (P1, P2, P3)
exchange messages; each process keeps a logical clock, and the scripts print every event
in one global order together with its timestamp. The processes are MPI ranks (rank 0 =
P1, rank 1 = P2, rank 2 = P3) and the messages are sent with `mpi4py`.

## Files

| File | What it is |
|------|------------|
| `lamport_clock.py` | The `LamportClock` class (one integer counter). |
| `vector_clock.py` | The `VectorClock` class (one counter per process) and the helpers to compare two vectors. |
| `lamport_test.py` | Lamport clock on the "Lamport's Clock: Example" slide (m1: P2 to P1, m2: P1 to P3, a local event in P1 and in P3), one MPI rank per process. |
| `vector_test_1.py` | Vector clock, Case 1 of the "Vector Clock: Two Cases" slide. |
| `vector_test_2.py` | Vector clock, Case 2 of the "Vector Clock: Two Cases" slide. |

Each clock class is in its own file and can also be run alone
(`python3 lamport_clock.py`, `python3 vector_clock.py`) for a small demo.

## Requirements

* Python 3.8 or later
* An MPI implementation (Open MPI or MPICH), e.g. `sudo apt install openmpi-bin`
* mpi4py: `pip install mpi4py`

## How to run

Always use exactly 3 ranks:

```
mpirun -n 3 python3 lamport_test.py        # Lamport clock
mpirun -n 3 python3 vector_test_1.py       # vector clock, case 1
mpirun -n 3 python3 vector_test_2.py       # vector clock, case 2
```

If the machine has fewer than 3 cores, add `--oversubscribe` after `mpirun`.
If you run as root (e.g. in a container), add `--allow-run-as-root`.

## Output

```
Vector clock, case 1 -- events in order
 1. P2 sends m1 to P1            -> [0, 1, 0]
 2. P1 receives m1 [0, 1, 0]     -> [1, 1, 0]
 ...
```

Each line is one event: its number in the global order, what happened, and the
timestamp the process computed (for Lamport, the counters of all three processes as a list `C = [C1, C2, C3]` right after the event, so `C = [2, 1, 0]` means P1's counter is 2, P2's is 1 and P3's is 0; for vector clocks, the vector the process computed).
Each rank also checks its own timestamps against the values on the slide; the script
stops with an assertion error if one differs.

## The rules

Lamport clock: before an event, `C += 1`; a message carries the sender's new counter
`ts(m)`; on receive, `C = max(C, ts(m))` and then `C += 1`.

Vector clock: before an event, `VC[i] += 1`; a message carries a copy of the whole
vector; on receive, `VC[k] = max(VC[k], ts(m)[k])` for every k and then `VC[i] += 1`.

## How the events are ordered

* Lamport: sorted by (counter, process number). A cause always has a smaller counter
  than its effect.
* Vector: sorted by the sum of the vector's entries. A cause always has a smaller sum
  than its effect. Events with equal sums are concurrent, so their order is arbitrary
  (the script lists the higher process number first, to make the output reproducible).
