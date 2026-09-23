# Lecture 7 -- Message Passing

Companion code for Lecture 7 ("Message Passing"): transient (socket-based) messaging,
persistent message queuing, message brokers, and MPI point-to-point communication.

All scripts require **Python 3.9+** and the standard library only, except the `MPI/`
subdirectory, which additionally requires `mpi4py` and an MPI runtime (see below).

| Subdirectory | Topic | Slides |
|---|---|---|
| [`Socket/`](Socket/) | Transient messaging with raw TCP sockets (client/server) | Berkeley Socket Interface |
| [`Message-Queue/`](Message-Queue/) | Persistent messaging with a queue: PUT/GET, NOTIFY, POLL | Message-Oriented Middleware, Queue Interface |
| [`Message-Queue-With-Broker/`](Message-Queue-With-Broker/) | A broker sitting between sender and receiver, translating message format | Message Broker |
| [`MPI/`](MPI/) | The 8 core MPI point-to-point operations (`SEND`/`BSEND`/`SSEND`/`SENDRECV`/`ISEND`/`ISSEND`/`RECV`/`IRECV`) via `mpi4py` | MPI Operations |

Each subdirectory has its own README with a script table and run instructions.

All example code is adapted for classroom use from *Distributed Systems*, 4th ed.
(Van Steen & Tanenbaum) and standard `mpi4py`/socket/queuing patterns; it is not the
instructor's original copyright and is included here for instructional attribution only.
