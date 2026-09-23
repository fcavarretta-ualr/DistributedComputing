from mpi4py import MPI                          # import the mpi4py bindings to MPI
comm = MPI.COMM_WORLD                            # get the default communicator (all launched processes)
rank = comm.Get_rank()                           # comm.Get_rank() -> int: this process's unique ID (0, 1, ...)

if rank == 0:                                    # branch: code only rank 0 runs
    comm.send("a message that recv is waiting for", dest=1, tag=0)  # MPI_SEND: blocking send; returns None once copied to a buffer
elif rank == 1:                                  # branch: code only rank 1 runs
    print(f"[Rank {rank}] Blocking here until a message arrives...")  # printed before the blocking call
    data = comm.recv(source=0, tag=0)            # MPI_RECV: blocks the process until a matching message shows up; returns the sent object
    print(f"[Rank {rank}] Unblocked! Received: {data}")  # only prints once recv has unblocked
else:                                             # branch: any rank other than 0 or 1 
    print(f"Unknown Rank {rank}")    
    
