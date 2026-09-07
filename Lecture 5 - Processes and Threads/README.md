# Lecture 5 — Threads and Processes

Code examples supporting the Threads and Processes lecture: how processes
and threads differ, and how they're used for concurrency in a small
client/server system.

| Script | Demonstrates |
|---|---|
| `multiprocessing_example.py` | Running the same function in two separate OS processes, each with its own private memory, launched with `.start()` and synchronized with `.join()`. |
| `multithreading_example.py` | The same pattern with two threads in one process instead — a direct comparison, since threads share the process's memory. |
| `client_server_example.py` | A client and server (a pizzeria taking orders) as two processes talking over a socket via `Listener`/`Client`, with a shared `Queue` for ordered logging. |

## Running the Examples

Requires Python 3, no extra packages:

```bash
python3 multiprocessing_example.py
python3 multithreading_example.py
python3 client_server_example.py
```

`client_server_example.py` launches both the server and the client itself, so
no separate setup is needed.
