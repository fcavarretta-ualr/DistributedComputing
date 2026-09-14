# Remote Procedure Calls (RPC)

Code example supporting the RPC lecture material: a client that invokes a
method on a remote server almost as if it were a local function call, using
[RPyC](https://rpyc.readthedocs.io/) to hide the underlying socket
communication, marshalling, and stubs.

| Script | Demonstrates |
|---|---|
| `RPC_Server.py` | Exposes a small service (`DBListService`) over RPyC. Each connecting client gets its own server-side list. `exposed_append(data)` and `exposed_get_value()` are the only methods reachable remotely -- the `exposed_` prefix is what RPyC uses to decide which methods a client stub is allowed to call. |
| `RPC_Client.py` | Connects to the server and calls `append(2)`, `append(4)`, and `get_value()` as ordinary method calls (`connection.root.<method>(...)`) -- RPyC's client stub packs each call into a message, sends it, and unpacks the reply, so the program never touches a socket directly. |

## How this maps to the lecture concepts

- **Access transparency**: the client calls `connection.root.append(2)` the
  same way it would call a local method -- there is no explicit `send()`/
  `receive()` in the client code.
- **Client stub / server stub**: RPyC generates these automatically. The
  client stub (`connection.root`) marshals the method name and arguments
  into a message; on the server, RPyC's dispatcher unmarshals the message
  and invokes the matching `exposed_` method locally.
- **Synchronous RPC**: each call (`append`, `get_value`) blocks until the
  server's reply comes back, matching the synchronous RPC model from the
  lecture.

## Running the Example

Requires Python 3 and the `rpyc` package:

```bash
pip install rpyc
```

Start the server first, then the client, each in its own terminal:

```bash
python3 RPC_Server.py
```

```bash
python3 RPC_Client.py
```

Expected client output:

```
Connected to the RPC server.
After appending 2: [2]
After appending 4: [2, 4]
Final server list: [2, 4]
Connection closed.
```

The server logs each connection and appended value, and keeps running
(`Ctrl+C` to stop it) so multiple client runs can be tried against it -- each
new client connection starts with its own fresh list.
