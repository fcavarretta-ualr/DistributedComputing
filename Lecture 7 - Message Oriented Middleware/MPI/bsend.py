from mpi4py import MPI                          # import the mpi4py bindings to MPI
comm = MPI.COMM_WORLD                            # get the default communicator (all launched processes)
rank = comm.Get_rank()                           

# Every rank that will call bsend must first attach a buffer big enough
# to hold the message.
BUFFER_SIZE = 10_000                             # size in bytes of the buffer bsend will copy messages into
buf = MPI.Alloc_mem(BUFFER_SIZE)                 # MPI.Alloc_mem(size) -> buffer object: allocates BUFFER_SIZE bytes of raw memory
MPI.Attach_buffer(buf)                           # MPI.Attach_buffer(buf) -> None: registers buf as the buffer future bsend calls will use

if rank == 0:                                    # branch: code only rank 0 runs
    data = {"msg": "buffered hello"}             # the Python object we will send
    comm.bsend(data, dest=1, tag=0)              # MPI_BSEND: copies data into the attached buffer and returns immediately (None)
    print(f"[Rank {rank}] bsend returned immediately, message is sitting in the buffer")  # confirm bsend did not block
elif rank == 1:                                  # branch: code only rank 1 runs
    data = comm.recv(source=0, tag=0)            # MPI_RECV: blocks until the buffered message arrives; returns the sent object
    print(f"[Rank {rank}] Received: {data}")     # confirm what rank 1 received
else:                                             # branch: any rank other than 0 or 1 
    print(f"Unknown Rank {rank}")    
    

MPI.Detach_buffer()                              # MPI.Detach_buffer() -> buffer object: unregisters the buffer (waits for pending bsends to finish)
MPI.Free_mem(buf)                                # MPI.Free_mem(buf) -> None: releases the raw memory back to the system
