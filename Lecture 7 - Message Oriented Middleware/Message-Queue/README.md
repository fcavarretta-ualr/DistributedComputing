# Message-Queue -- Persistent Messaging (PUT/GET, NOTIFY, POLL)

Three variations on **persistent** messaging through a shared in-memory queue
(`queue.Queue`), where sender and receiver do not need to be active at the same
instant -- the queue holds the message until the receiver is ready. Each script
runs sender and receiver as two threads of the same process, standing in for two
separate applications talking through a queue manager.

| Script | Pattern | Description |
|---|---|---|
| `message_queue_demo.py` | PUT / GET | Sender PUTs three messages plus a `STOP` sentinel; receiver GETs in a loop (GET blocks until a message is available) until it sees `STOP`. |
| `message_queue_NOTIFY.py` | NOTIFY | Receiver blocks on a `threading.Event`; sender PUTs a message and then sets the event, waking the receiver immediately. |
| `message_queue_POLL.py` | POLL (bounded) | Receiver checks the queue at 1-second intervals for up to 8 iterations rather than blocking; reports timeout if nothing arrives in time. |

## How to run

Each script is self-contained -- no server or second terminal needed:

```bash
python3 message_queue_demo.py
python3 message_queue_NOTIFY.py
python3 message_queue_POLL.py
```

`message_queue_demo.py` prints an interleaved log of sends/receives ending in
"Program Finished". `message_queue_NOTIFY.py` prints a short wait-then-receive
sequence. `message_queue_POLL.py` prints a few "No message available" polls
(since the sender sleeps 5s before sending) followed by "Received: ...".

Verified end-to-end -- all three run cleanly to completion with the expected output.
