"""
===========================================================
Fig-4.8-Example- A simple RPC example for operation append.
===========================================================
channel.py — TRANSPORT LAYER + PROTOCOL CONSTANTS

Simulates the transport layer of an RPC system using two in-memory queues.
In a real RPC system this would be replaced by TCP sockets, HTTP, or a
message broker like RabbitMQ.

Also defines the protocol constants (like APPEND) that identify remote
operations on the wire. Both Client and Server import these constants so
they agree on which operation is being requested.
"""


# Import the queue module to simulate communication between client and server.
import queue


# ---------------------------------------------------------------------------
# Protocol constants — the "wire format" for identifying remote procedures.
# Both Client and Server import these so they agree on message contents.
# ---------------------------------------------------------------------------

# Define a constant representing the remote operation.
APPEND = "APPEND"


# ---------------------------------------------------------------------------
# Channel — the shared transport between client and server.
# ---------------------------------------------------------------------------

# Define a communication channel between client and server.
class Channel:

    # Constructor to initialize communication queues.
    def __init__(self):

        # Queue used for sending requests from client to server.
        self.request_queue = queue.Queue()

        # Queue used for sending responses from server to client.
        self.response_queue = queue.Queue()

    # Method used by the client to send a request to the server.
    def send_to_server(self, sender, message):

        # Store sender ID and message in the request queue.
        self.request_queue.put((sender, message))

    # Method used by the server to receive requests.
    def receive_from_any(self):

        # Wait until a request arrives and return it.
        return self.request_queue.get()

    # Method used by the server to send a response back to the client.
    def send_to_client(self, client, message):

        # Store the response in the response queue.
        self.response_queue.put((client, message))

    # Method used by the client to receive the server's response.
    def receive_from_server(self, client):

        # Wait until a response arrives.
        receiver, message = self.response_queue.get()

        # Check that the response belongs to the correct client.
        if receiver != client:

            # Raise an error if another client's response is received.
            raise RuntimeError("Response was sent to the wrong client.")

        # Return the sender name and received message.
        return "server", message
