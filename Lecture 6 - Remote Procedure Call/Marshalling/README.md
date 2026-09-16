# Fig 4.9 — RPC Marshalling

Same `APPEND`-over-a-shared-list RPC simulation as [Fig 4.8](../Fig-4.8-RPCWithAppend),
but this version makes marshalling explicit: the client and server stubs
`pickle`/`unpickle` the call and its arguments instead of passing live Python
objects through the channel. Paired with Fig 4.8 specifically to contrast
what marshalling is for.

## The five files

Same architectural split as Fig 4.8:

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
