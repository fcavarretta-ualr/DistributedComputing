# Fig 4.8 — RPC with Append

A hand-rolled RPC simulation illustrating an `APPEND` remote call against a
shared list, split across five files by architectural role.

## The five files

| File | Role in RPC architecture | Contents |
|---|---|---|
| `dblist.py` | Data layer | The `DBList` class — the "database" being manipulated |
| `channel.py` | Transport + protocol | The `Channel` class + the `APPEND` constant |
| `client.py` | Client stub | The `Client` class that marshals calls and awaits responses |
| `server.py` | Server dispatcher | The `Server` class that receives, decodes, and dispatches |
| `main.py` | Entry point | The `main()` function that wires everything together |

## How the imports flow (dependency graph)

```
main.py ─┬─→ channel.py
         ├─→ client.py ─→ channel.py (for APPEND)
         ├─→ server.py ─→ channel.py (for APPEND)
         └─→ dblist.py
```

`channel.py` is at the bottom because it defines the protocol constants that
everyone else needs. `dblist.py` is completely standalone — it doesn't know
anything about RPC. `client.py` and `server.py` sit on top, each importing
what they need. `main.py` pulls everything together.

## How to run

All five files must be in the same folder. Then, from that folder:

```bash
python main.py
```

## Expected output

```
Before RPC call: DBList([10, 20, 30])
After RPC call: DBList([10, 20, 30, 40, 50])
```
