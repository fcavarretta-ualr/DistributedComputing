from mpi4py import MPI                          # import the mpi4py bindings to MPI
import time                                      # used to simulate rank 1 being busy before it receives
comm = MPI.COMM_WORLD                            # get the default communicator (all launched processes)
rank = comm.Get_rank()                           # comm.Get_rank() -> int: this process's unique ID (0, 1, ...)

if rank == 0:                                    # branch: code only rank 0 runs
    data = "non-blocking synchronous hello"      # the Python object we will send
    req = comm.issend(data, dest=1, tag=0)       # MPI_ISSEND: starts a non-blocking synchronous send; returns an MPI.Request handle immediately
    print(f"[Rank {rank}] issend issued, request not yet complete")  # proves issend did not block at call time
    req.wait()                                   # request.wait() -> None: blocks until rank 1 has started receiving
    print(f"[Rank {rank}] issend confirmed: receiver has started receiving")  # only prints after the handshake completes
elif rank == 1:                                  # branch: code only rank 1 runs
    time.sleep(1)                                # simulate the receiver being busy first, so issend's wait() visibly blocks
    data = comm.recv(source=0, tag=0)            # MPI_RECV: blocks until a matching message arrives; returns the sent object
    print(f"[Rank {rank}] Received: {data}")     # confirm what rank 1 received
else:                                             # branch: any rank other than 0 or 1 
    print(f"Unknown Rank {rank}")
