# Embedding RPCs

A real network RPC client/server pair built on [RPyC](https://rpyc.readthedocs.io/),
showing how RPC is embedded directly into a host language (Python) rather
than simulated over a hand-rolled protocol.

## Files

| File | Role |
|---|---|
| `RPC_Server.py` | Starts an RPyC `ThreadedServer` exposing a service on `localhost:18861` |
| `RPC_Client.py` | Connects to the server and calls its exposed methods as if they were local |

## Requirements

```bash
pip install rpyc
```

## How to run

In one terminal:

```bash
python RPC_Server.py
```

In another terminal:

```bash
python RPC_Client.py
```

## Expected output

Server side confirms the client connected and shows each value appended;
client side prints the running list after each remote append, e.g.:

```
Connected to the RPC server.
After appending 2: [2]
After appending 4: [2, 4]
Final server list: [2, 4]
Connection closed.
```
