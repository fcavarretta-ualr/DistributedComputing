"""
===========================================================================================
Fig-4.9-Example- A simple RPC example for operation append with proper marshaling.
===========================================================================================

client.py — CLIENT STUB (with marshalling)

The stub still makes RPC calls "look local," but now it does two extra
steps that weren't in the previous version:
  1. MARSHAL — before sending, serialize the message to bytes with pickle
  2. UNMARSHAL — after receiving, deserialize the response bytes back to
     a Python object

This is the pattern every real RPC framework uses. XML-RPC marshals to XML,
gRPC marshals to Protocol Buffers, JSON-RPC marshals to JSON. Pickle is
Python-only, but the *structure* of the code is identical to any of them.
"""


# Import pickle for marshaling (serialization) and unmarshaling.
import pickle

# Import the APPEND protocol constant from the channel module.
from channel import APPEND


# Client Stub
class Client:

    # Constructor.
    def __init__(self, channel):

        # Communication channel.
        self.channel = channel

        # Server identifier.
        self.server = "server"

    # Remote append procedure.
    def append(self, data, dbList):

        # Create RPC request tuple.
        msglst = (APPEND, data, dbList)

        # Marshal (serialize) the request into a bytes stream that could,
        # in principle, be sent over any byte-oriented channel (a TCP
        # socket, a pipe, a file, or — as here — an in-memory queue).
        msgsnd = pickle.dumps(msglst)

        # Send serialized request to the server.
        self.channel.sendTo(self.server, msgsnd)

        # Wait for the server response.
        msgrcv = self.channel.recvFrom(self.server)

        # Unmarshal (deserialize) the received response back into a
        # Python object we can use.
        retval = pickle.loads(msgrcv[1])

        # Return the updated object.
        return retval
