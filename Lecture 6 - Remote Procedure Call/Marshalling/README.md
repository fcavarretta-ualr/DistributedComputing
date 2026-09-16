# RPC Marshalling

Same `APPEND`-over-a-shared-list RPC simulation as [Append](../WithAppend),
but this version makes marshalling explicit: the client and server stubs
`pickle`/`unpickle` the call and its arguments instead of passing live Python
objects through the channel. 

## The five files

| File | Layer | Contents |
|---|---|---|
| `dblist.py` | Data | `DBList` class (identical to the previous version) |
| `channel.py` | Transport + protocol | `Channel` class + `APPEND` constant |
| `client.py` | Client stub | `Client` class + `import pickle` |
| `server.py` | Server dispatcher | `Server` class + `import pickle` |
| `main.py` | Entry point | `main()` function |

## How to run

Put all five files in the same folder, then from that folder:

```bash
python main.py
```

## Expected output

```
Before RPC: DBList([10, 20, 30])
After RPC : DBList([10, 20, 30, 40, 50])
```
