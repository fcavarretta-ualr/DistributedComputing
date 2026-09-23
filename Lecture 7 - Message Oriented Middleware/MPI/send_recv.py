from mpi4py import MPI                          # import the mpi4py bindings to MPI
comm = MPI.COMM_WORLD                            # get the default communicator (all launched processes)
rank = comm.Get_rank()                           

if rank == 0:                                    # branch: code only rank 0 runs
    data = {"msg": "hello", "value": 42}         # the Python object we will send (any picklable object works)
    comm.send(data, dest=1, tag=0)               # MPI_SEND: blocking send; returns None once data is copied to a buffer
    print(f"[Rank {rank}] Sent: {data}")         # confirm what rank 0 sent
elif rank == 1:                                  # branch: code only rank 1 runs
    data = comm.recv(source=0, tag=0)            # MPI_RECV: blocks until a matching message arrives; returns the sent object
    print(f"[Rank {rank}] Received: {data}")     # confirm what rank 1 received
else:                                             # branch: any rank other than 0 or 1 
    print(f"Unknown Rank {rank}")                # safety net so unexpected ranks don't fail silently
