from mpi4py import MPI                          # import the mpi4py bindings to MPI
comm = MPI.COMM_WORLD                            # get the default communicator (all launched processes)
rank = comm.Get_rank()                           # comm.Get_rank() -> int: this process's unique ID (0, 1, ...)

partner = 1 - rank                               # compute the other rank's ID: rank 0 <-> rank 1

sent_data = f"hello from {rank}"                 # the Python object this rank will send to its partner
received_data = comm.sendrecv(sent_data, dest=partner, sendtag=0,   # MPI_SENDRECV: sends sent_data to `partner`
                               source=partner, recvtag=0)            # ...and simultaneously receives a reply from `partner`; returns the received object

print(f"[Rank {rank}] Sent: '{sent_data}'  |  Received: '{received_data}'")  # show both halves of the exchange
