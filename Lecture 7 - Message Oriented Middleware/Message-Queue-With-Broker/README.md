# Message-Queue-With-Broker -- Message Broker

Extends the queue-based examples with a **broker** sitting between sender and
receiver: `Sender -> Input Queue -> Broker -> Output Queue -> Receiver`. The
broker's job is to translate the message format the sender uses into the format
the receiver expects, so the two applications don't need to agree on one shared
format themselves.

| Script | Description |
|---|---|
| `MessageQueueWithBroker.py` | Sender PUTs a pipe-delimited string (`"john\|25\|USA"`) into the input queue. The broker GETs it, splits and converts it into a `dict` (`{"name": ..., "age": ..., "country": ...}`), and PUTs the converted message into the output queue. The receiver GETs the converted dict from the output queue. |

## How to run

```bash
python3 MessageQueueWithBroker.py
```

Expected output:

```
Sender sent: john|25|USA
Broker received: john|25|USA
Broker converted: {'name': 'john', 'age': '25', 'country': 'USA'}
Receiver received: {'name': 'john', 'age': '25', 'country': 'USA'}
Communication completed.
```

Verified end-to-end -- runs cleanly to completion with the expected output.
