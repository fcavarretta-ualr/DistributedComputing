"""
===========================================================================================
Fig-4.9-Example- A simple RPC example for operation append with proper marshaling.
===========================================================================================
channel.py — TRANSPORT LAYER + PROTOCOL CONSTANTS

Simulates the transport with in-memory queues. Unlike a real network
transport, these queues carry Python objects directly — but because the
client and server marshal messages to bytes before putting them on the
channel, the transport itself only ever sees BYTES. That's the same
constraint a real TCP socket has, which is why this simulation is a
faithful model of real RPC in that respect.

Also defines the protocol constants (APPEND) that identify remote
operations. Both Client and Server import these so they agree on the
"wire format."
"""


# Import queue module to simulate communication between client and server.
import queue


# ---------------------------------------------------------------------------
# Protocol constants — the "wire format" for identifying remote procedures.
# ---------------------------------------------------------------------------

# Define the RPC operation name.
APPEND = "APPEND"


# ---------------------------------------------------------------------------
# Channel — the shared transport between client and server.
# ---------------------------------------------------------------------------

# Communication channel.
class Channel:

    # Constructor.
    def __init__(self):

        # Queue for client requests.
        self.request_queue = queue.Queue()

        # Queue for server responses.
        self.response_queue = queue.Queue()

    # Send request to the server.
    def sendTo(self, receiver, message):

        # If receiver is the server, store request.
        if receiver == "server":
            self.request_queue.put(("client", message))

        # Otherwise, send response to the client.
        else:
            self.response_queue.put((receiver, message))

    # Server receives request.
    def recvFromAny(self):

        # Wait until a request arrives.
        return self.request_queue.get()

    # Client receives response.
    def recvFrom(self, sender):

        # Wait until a response arrives.
        return self.response_queue.get()
