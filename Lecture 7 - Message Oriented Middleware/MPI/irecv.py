from mpi4py import MPI                          # import the mpi4py bindings to MPI
import time                                      # used to simulate rank 0 delaying its send
comm = MPI.COMM_WORLD                            # get the default communicator (all launched processes)
rank = comm.Get_rank()                           # comm.Get_rank() -> int: this process's unique ID (0, 1, ...)

if rank == 0:                                    # branch: code only rank 0 runs
    time.sleep(1)                                # simulate rank 0 being slow to send, so rank 1's irecv has time to "do other work"
    comm.send("delayed hello", dest=1, tag=0)    # MPI_SEND: blocking send; returns None once copied to a buffer
elif rank == 1:                                  # branch: code only rank 1 runs
    req = comm.irecv(source=0, tag=0)            # MPI_IRECV: posts a non-blocking receive; returns an MPI.Request handle immediately (no message yet)
    print(f"[Rank {rank}] irecv posted, doing other work while waiting...")  # proves irecv did not block at call time
    # ... you could do useful computation here ...
    data = req.wait()                            # request.wait() -> object: blocks until the message arrives, then returns it
    print(f"[Rank {rank}] Received: {data}")     # confirm what rank 1 received
else:                                             # branch: any rank other than 0 or 1 
    print(f"Unknown Rank {rank}")    
