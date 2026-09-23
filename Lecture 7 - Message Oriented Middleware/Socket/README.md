# Socket -- Transient Messaging (Berkeley Sockets)

A minimal client/server pair over a raw TCP socket, illustrating **transient**
communication: both processes must be up and connected at the same time, or the
exchange doesn't happen. The client sends one message; the server echoes it back
with a trailing `*` and closes the connection.

| Script | Role | Description |
|---|---|---|
| `SocketBased-Server.py` | Server | Binds `127.0.0.1:5000`, listens for one connection, receives a message, sends it back with `*` appended, then shuts down. |
| `SocketBased-Client.py` | Client | Connects to `127.0.0.1:5000`, sends `"Hello, world"`, prints the echoed reply, closes the connection. |

## How to run

Start the server first, in its own terminal:

```bash
python3 SocketBased-Server.py
```

Then, in a second terminal, run the client:

```bash
python3 SocketBased-Client.py
```

Expected server output:

```
Server is listening on 127.0.0.1:5000...
Connected by client: ('127.0.0.1', <port>)
Received: Hello, world
Sent: Hello, world*
Client closed the connection.
Server stopped.
```

Expected client output:

```
Connecting to server at 127.0.0.1:5000...
Sent: Hello, world
Received: Hello, world*
Client connection closed.
```

Verified end-to-end (server + client run concurrently, full echo exchange confirmed).
