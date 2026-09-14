# Import the queue module to simulate communication between client and server.
import queue

# Import threading module to run the server and client simultaneously.
import threading

# Define a constant representing the remote operation.
APPEND = "APPEND"


# Define a class that represents a database list stored on the server.
class DBList:

    # Constructor to initialize the database list.
    def __init__(self, initial_values=None):

        # Create the internal list. If initial values exist, copy them;
        # otherwise create an empty list.
        self.value = list(initial_values) if initial_values else []

    # Method to append data into the database list.
    def append(self, data):

        # Add all elements from 'data' into the internal list.
        self.value.extend(data)

        # Return the updated object.
        return self

    # Define how the object will be displayed when printed.
    def __repr__(self):

        # Return the list in a readable format.
        return f"DBList({self.value})"


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


# Main function where program execution starts.
def main():

    # Create the communication channel.
    channel = Channel()

    # Create the server object.
    server = Server(channel)

    # Create a separate thread for the server.
    server_thread = threading.Thread(target=server.run, daemon=True)

    # Start the server thread.
    server_thread.start()

    # Create a client object.
    client = Client("Client-1", channel)

    # Create a database list with initial values.
    database_list = DBList([10, 20, 30])

    # Display the original list.
    print("Before RPC call:", database_list)

    # Client requests the server to append new values.
    updated_list = client.append([40, 50], database_list)

    # Display the updated list returned by the server.
    print("After RPC call:", updated_list)

    # Send a STOP request to terminate the server.
    channel.send_to_server("Client-1", ("STOP", None, None))

    # Wait until the server thread finishes execution.
    server_thread.join()


# Check whether this file is being executed directly.
if __name__ == "__main__":

    # Start the program.
    main()