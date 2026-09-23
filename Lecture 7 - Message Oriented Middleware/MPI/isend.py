from mpi4py import MPI                          # import the mpi4py bindings to MPI
comm = MPI.COMM_WORLD                            # get the default communicator (all launched processes)
rank = comm.Get_rank()                           # comm.Get_rank() -> int: this process's unique ID (0, 1, ...)

if rank == 0:                                    # branch: code only rank 0 runs
    data = "non-blocking hello"                  # the Python object we will send
    req = comm.isend(data, dest=1, tag=0)        # MPI_ISEND: starts a non-blocking send; returns an MPI.Request handle immediately
    print(f"[Rank {rank}] isend issued, doing other work while it completes...")  # proves isend did not block
    # ... you could do useful computation here ...
    req.wait()                                   # request.wait() -> None: blocks until the isend has actually completed
    print(f"[Rank {rank}] isend confirmed complete")  # only prints after the send is truly done
elif rank == 1:                                  # branch: code only rank 1 runs
    data = comm.recv(source=0, tag=0)            # MPI_RECV: blocks until a matching message arrives; returns the sent object
    print(f"[Rank {rank}] Received: {data}")     # confirm what rank 1 received
else:                                             # branch: any rank other than 0 or 1 
    print(f"Unknown Rank {rank}")    
