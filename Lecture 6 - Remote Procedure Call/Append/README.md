# Remote Procedure Calls (RPC)

Code examples supporting the RPC lecture material: a client that invokes a
method on a server almost as if it were a local function call, hiding the
underlying communication, marshalling, and stubs behind an ordinary-looking
method call.

Both scripts here simulate RPC in a single process -- the "client" and
"server" are two threads sharing an in-memory `Channel` (built from a pair
of `queue.Queue` objects) instead of talking over a real socket. Each still
has the same shape as a real RPC: a `Client` (client stub) that packages a
request and hands it to the channel, and a `Server` that receives requests,
runs the matching local method, and sends the result back.

| Script | Demonstrates |
|---|---|
| `RPC-AppendWithMarshalling.py` | The same append example, but WITH explicit marshalling/unmarshalling via `pickle`. |
| `RPC-Example-Append.py` | The append example WITHOUT marshalling -- objects are passed directly through the queue. Comparing it to `RPC-AppendWithMarshalling.py` shows what marshalling is actually for. |

Each script appends `[40, 50]` to a `DBList` that starts as `[10, 20, 30]`:

```
Before RPC call: DBList([10, 20, 30])
After RPC call: DBList([10, 20, 30, 40, 50])
```

The difference between the two is what happens to the request/response on
the way through the channel:

- **`RPC-AppendWithMarshalling.py`** actually marshals: the client packs the
  operation name and arguments into a tuple and serializes it with
  `pickle.dumps()` before handing it to the channel, and the server calls
  `pickle.loads()` to reconstruct it before executing the operation (and
  marshals the result the same way before sending it back). This mirrors
  what a real RPC system must do to cross a process or machine boundary,
  even though here everything is still in one process.
- **`RPC-Example-Append.py`** skips marshalling entirely -- the request
  tuple and the `DBList` object are passed straight through the queue as
  live Python objects. That only works because the client and server share
  the same process's memory; it would not work across a real network, which
  is exactly the point of comparing it against the marshalling version. It
  also adds a client ID and a basic correctness check (the channel raises an
  error if a response meant for one client is delivered to another), and
  handles the `"STOP"` operation as a normal message rather than a special
  sentinel value.

## Running the Examples

Requires Python 3, no extra packages:

```bash
python3 RPC-AppendWithMarshalling.py
python3 RPC-Example-Append.py
```

Each script starts its own server thread, runs one client call, then stops
the server and exits -- no separate setup needed.
