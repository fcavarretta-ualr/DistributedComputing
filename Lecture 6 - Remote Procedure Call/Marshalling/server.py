"""
===========================================================================================
Fig-4.9-Example- A simple RPC example for operation append with proper marshaling.
===========================================================================================
server.py — SERVER DISPATCHER (with marshalling)

Mirror of the client: every message coming in from the channel is bytes,
so the server must UNMARSHAL it before it can inspect the operation, and
MARSHAL the result before sending it back.

One special case: the STOP message is checked in its raw byte form
(b"STOP") BEFORE attempting to unmarshal. This is a shortcut — it avoids
needing to define a proper serialized STOP request.
"""


# Import pickle for marshaling and unmarshaling messages.
import pickle

# Import the APPEND protocol constant from channel — the server needs
# it to recognize which operation an incoming message is asking for.
from channel import APPEND


# Server
class Server:

    # Constructor.
    def __init__(self, channel):

        # Communication channel.
        self.channel = channel

        # Server running flag.
        self.running = True

    # Local append procedure.
    def append(self, data, dbList):

        # Perform append locally.
        return dbList.append(data)

    # Server loop.
    def run(self):

        # Continue until stopped.
        while self.running:

            # Wait for client request.
            msgreq = self.channel.recvFromAny()

            # Identify the client.
            client = msgreq[0]

            # Stop request — checked in raw byte form BEFORE unmarshalling.
            # A pickled STOP would work too, but this shortcut keeps the
            # shutdown path free of pickle dependencies.
            if msgreq[1] == b"STOP":
                self.running = False
                break

            # Unmarshal the received request from bytes back into a
            # Python tuple.
            msgrpc = pickle.loads(msgreq[1])

            # Check requested operation.
            if APPEND == msgrpc[0]:

                # Execute the local append procedure.
                result = self.append(msgrpc[1], msgrpc[2])

                # Marshal the result into bytes for transport back.
                msgres = pickle.dumps(result)

                # Send serialized result back to the client.
                self.channel.sendTo(client, msgres)
