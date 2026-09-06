<p align="center">
  <img src="banner-murmuration.png" alt="Starling murmuration" width="700">
</p>

# Distributed Computing -- Code Examples

Code examples shared during lectures for the Distributed Computing course
(CPSI 48703/58703), University of Arkansas at Little Rock, taught by
Francesco Cavarretta. This repo grows over time as new examples are
introduced in class.

Course material follows Andrew S. Tanenbaum and Maarten van Steen,
*Distributed Systems*, 4th ed. -- see the book's companion site at
[distributed-systems.net](https://www.distributed-systems.net/index.php/books/ds4/).

## Lecture 5 -- Threads and Processes

**multiprocessing_example.py** -- Runs the same function twice, each in its
own separate OS process. Shows how `multiprocessing.Process` spawns
independent processes with private memory, started concurrently with
`.start()` and synchronized with `.join()`.

**multithreading_example.py** -- Runs the same function twice, each in its
own thread within one process. Mirrors the multiprocessing example so the
two can be compared directly, but here the threads share the process's
memory space.

**client_server_example.py** -- A pizzeria simulation: a server process
takes orders and a client process places them, talking over a socket
connection via `multiprocessing.connection`'s `Listener`/`Client`. A shared
`Queue` collects both processes' log messages so they print in the order
things actually happened.

## Running the examples

Requires Python 3, no extra packages. Run any file directly:

```
python3 multiprocessing_example.py
python3 multithreading_example.py
python3 client_server_example.py
```

`client_server_example.py` starts both the server and the client as
processes within the same run, so no separate setup is needed.
