from mpi4py import MPI                          # import the mpi4py bindings to MPI
import time                                      # used to simulate rank 1 being busy before it receives
comm = MPI.COMM_WORLD                            # get the default communicator (all launched processes)
rank = comm.Get_rank()                           # comm.Get_rank() -> int: this process's unique ID (0, 1, ...)

if rank == 0:                                    # branch: code only rank 0 runs
    data = "synchronous hello"                   # the Python object we will send
    print(f"[Rank {rank}] About to ssend...")    # marker printed before the (potentially slow) ssend call
    comm.ssend(data, dest=1, tag=0)              # MPI_SSEND: blocks until rank 1 has started its matching recv; returns None
    print(f"[Rank {rank}] ssend completed: receiver has started receiving")  # only prints after the handshake completes
elif rank == 1:                                  # branch: code only rank 1 runs
    time.sleep(1)                                # simulate the receiver being busy first, so ssend above visibly waits
    data = comm.recv(source=0, tag=0)            # MPI_RECV: blocks until a matching message arrives; returns the sent object
    print(f"[Rank {rank}] Received: {data}")     # confirm what rank 1 received
else:                                             # branch: any rank other than 0 or 1 
    print(f"Unknown Rank {rank}")    
