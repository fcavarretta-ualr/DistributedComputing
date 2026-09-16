"""

===========================================================
Fig-4.8-Example- A simple RPC example for operation append.
===========================================================
server.py — SERVER DISPATCHER

Runs a loop that:
  1. Receives incoming requests from the channel
  2. Decodes which operation was requested (looks at the message tag)
  3. Dispatches to the appropriate local method
  4. Sends the result back through the channel

This is the classic "server skeleton" of any RPC framework.
"""


# Import the APPEND protocol constant from channel — the server needs
# it to recognize which operation an incoming message is asking for.
from channel import APPEND


# Define the server class.
class Server:

    # Constructor to initialize the server.
    def __init__(self, channel):

        # Store the communication channel.
        self.channel = channel

        # Variable controlling whether the server keeps running.
        self.running = True

    # Actual append operation performed by the server.
    def append(self, data, db_list):

        # Call the DBList append() method locally.
        return db_list.append(data)

    # Server continuously waits for client requests.
    def run(self):

        # Continue running until stopped.
        while self.running:

            # Wait for an incoming client request.
            request = self.channel.receive_from_any()

            # Extract the client's ID.
            client_id = request[0]

            # Extract the RPC message.
            rpc_message = request[1]

            # Extract the requested operation.
            operation = rpc_message[0]

            # Check if the requested operation is APPEND.
            if operation == APPEND:

                # Extract the data parameter.
                data = rpc_message[1]

                # Extract the database list parameter.
                db_list = rpc_message[2]

                # Execute the requested operation locally.
                result = self.append(data, db_list)

                # Send the updated list back to the client.
                self.channel.send_to_client(client_id, result)

            # Check if the client wants to stop the server.
            elif operation == "STOP":

                # Stop the server loop.
                self.running = False
