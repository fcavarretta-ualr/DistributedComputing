# MPI -- Point-to-Point Communication Modes

`mpi_communication_modes.ipynb` walks through the 8 core MPI point-to-point
operations using `mpi4py`, each demonstrated with a tiny 2-rank program. The
notebook's code cells `%%writefile` each example to its own `.py` file and then
run it with `mpirun`/`mpiexec -n 2`; those generated scripts are also included
here directly so they can be run from a terminal without Jupyter.

| Script | MPI operation | Description |
|---|---|---|
| `send_recv.py` | `MPI_SEND` / `MPI_RECV` | The basic blocking pair: rank 0 sends a dict, rank 1 receives it. `send` returns once the message is copied to a buffer; `recv` blocks until a matching message arrives. |
| `bsend.py` | `MPI_BSEND` | Buffered send: rank 0 attaches a 10,000-byte buffer (`MPI.Attach_buffer`), then `bsend`s a dict, which returns immediately because the message is copied into that buffer rather than waiting on the receiver. |
| `ssend.py` | `MPI_SSEND` | Synchronous send: rank 1 sleeps 1s before calling `recv`, so rank 0's `ssend` visibly waits -- it only returns once rank 1 has *started* receiving (a real handshake). |
| `sendrecv.py` | `MPI_SENDRECV` | Both ranks 0 and 1 simultaneously send to and receive from each other in a single call -- the standard deadlock-free way to exchange data between two ranks. |
| `isend.py` | `MPI_ISEND` | Non-blocking send: rank 0's `isend` returns an `MPI.Request` immediately; `request.wait()` later confirms the send actually completed. |
| `issend.py` | `MPI_ISSEND` | Non-blocking synchronous send: returns a request immediately, but `request.wait()` only completes once rank 1 has started receiving (rank 1 sleeps 1s first so the wait is visible). |
| `recv_only.py` | `MPI_RECV` (recap) | Rank 1 calls `recv` and blocks until rank 0's `send` arrives -- isolates the blocking-receive behavior on its own. |
| `irecv.py` | `MPI_IRECV` | Non-blocking receive: rank 1 posts `irecv` and gets a request immediately (no message yet); rank 0 deliberately delays 1s before sending, so `request.wait()` visibly blocks until the message shows up. |

## Requirements

- `mpi4py` (`pip install mpi4py`)
- An MPI runtime providing `mpirun`/`mpiexec` (e.g. OpenMPI or MPICH)

## How to run

Every script needs **two ranks** to actually exchange a message -- running it
with plain `python3 script.py` just starts a single-process program that never
finds its partner. Launch each one with:

```bash
mpirun -n 2 python3 send_recv.py
mpirun -n 2 python3 bsend.py
mpirun -n 2 python3 ssend.py
mpirun -n 2 python3 sendrecv.py
mpirun -n 2 python3 isend.py
mpirun -n 2 python3 issend.py
mpirun -n 2 python3 recv_only.py
mpirun -n 2 python3 irecv.py
```

(`mpiexec -n 2 python3 <script>.py` is equivalent if your MPI distribution
prefers that name.) To step through the same examples with the explanatory
text alongside the code, open `mpi_communication_modes.ipynb` in Jupyter and
run its cells in order -- it detects the right launcher automatically.

Verified end-to-end: all 8 scripts were run with a genuine 2-process `mpirun -n 2`
launch (OpenMPI) and produced the expected rank-0/rank-1 output for each pattern.
Note: if `mpirun -n 2` ever reports both ranks as `size 1` instead of `size 2`,
that means the launcher failed to establish a real multi-process job (a
sandboxed/containerized environment issue we hit and traced to MPICH's default
launcher in one test setup) rather than a bug in the scripts -- switching to
OpenMPI's `mpirun`, or running on a normal (non-containerized) machine, resolved it.
