# Fig 4.20 — Implementing Stubs as Global References

Note 4.8: a demonstration of stubs implemented as global (remote) references.
Two clients and a server run as threads in the same process, and a remote
reference to a list is handed from Client 1 to Client 2, which then appends
to the same server-side list.

## Files

| File | Role |
|---|---|
| `config.py` | Shared constants — server/client host & port numbers, operation codes |
| `dbclient.py` | Figure 4.20 (a) — `DBClient`, the client-side stub for the remote list (create/append/get) |
| `server.py` | Figure 4.20 (b) — `Server`, listens for and handles remote list operations |
| `client.py` | Figure 4.20 (c) — `Client`, the low-level networking client used to send/receive raw data between Client 1 and Client 2 |
| `main.py` | Entry point — starts the server and both clients as threads; Client 1 creates a remote list and hands its reference to Client 2, which appends to it |

## How to run

From this folder:

```bash
python main.py
```

## Expected output

Client 1 creates a remote list, adds itself to it, and sends the remote
reference to Client 2 over a socket; Client 2 receives it, appends itself,
and both the client-side and server-side views of the list end up showing
`['Client 1', 'Client 2']`.
