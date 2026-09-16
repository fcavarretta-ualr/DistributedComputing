"""
===========================================================
Fig-4.8-Example- A simple RPC example for operation append.
===========================================================

client.py — CLIENT STUB

The stub is what makes RPC calls "look local." From the caller's perspective,
client.append(data, db_list) is just a method call. Internally the stub:
  1. Packages (marshalls) the arguments into a message
  2. Sends it through the transport channel
  3. Blocks waiting for the response
  4. Unwraps the response and returns the payload
"""


# Import the APPEND protocol constant from the channel module.
# The client needs it to label outgoing messages with the correct operation.
from channel import APPEND


# Define the client stub.
class Client:

    # Constructor to initialize the client.
    def __init__(self, client_id, channel):

        # Store the client's ID.
        self.client_id = client_id

        # Store the communication channel.
        self.channel = channel

    # Remote append procedure called by the client.
    def append(self, data, db_list):

        # Package the operation name and parameters into a tuple.
        message = (APPEND, data, db_list)

        # Send the RPC request to the server.
        self.channel.send_to_server(self.client_id, message)

        # Wait for the server's reply.
        received_message = self.channel.receive_from_server(self.client_id)

        # Return only the actual result.
        return received_message[1]
