# Import queue module to simulate communication between client and server.
import queue

# Import threading module to run the server in a separate thread.
import threading

# Import pickle module for marshaling (serialization) and unmarshaling (deserialization).
import pickle

# Define the RPC operation name.
APPEND = "APPEND"


# Database list stored on the server.
class DBList:

    # Constructor to initialize the database list.
    def __init__(self, initial_values=None):

        # Create an internal list.
        self.value = list(initial_values) if initial_values else []

    # Append new data to the database list.
    def append(self, data):

        # Add all elements from data to the list.
        self.value.extend(data)

        # Return the updated object.
        return self

    # Define how the object is displayed.
    def __repr__(self):

        # Return the object in readable form.
        return f"DBList({self.value})"


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

        # Marshal (serialize) the request.
        msgsnd = pickle.dumps(msglst)

        # Send serialized request to the server.
        self.channel.sendTo(self.server, msgsnd)

        # Wait for the server response.
        msgrcv = self.channel.recvFrom(self.server)

        # Unmarshal (deserialize) the received response.
        retval = pickle.loads(msgrcv[1])

        # Return the updated object.
        return retval


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

            # Stop request.
            if msgreq[1] == b"STOP":
                self.running = False
                break

            # Unmarshal the received request.
            msgrpc = pickle.loads(msgreq[1])

            # Check requested operation.
            if APPEND == msgrpc[0]:

                # Execute the local append procedure.
                result = self.append(msgrpc[1], msgrpc[2])

                # Marshal the result.
                msgres = pickle.dumps(result)

                # Send serialized result back to the client.
                self.channel.sendTo(client, msgres)


# Main program.
def main():

    # Create communication channel.
    channel = Channel()

    # Create server.
    server = Server(channel)

    # Start server thread.
    server_thread = threading.Thread(target=server.run)

    server_thread.start()

    # Create client.
    client = Client(channel)

    # Create sample database list.
    db = DBList([10, 20, 30])

    # Display original list.
    print("Before RPC:", db)

    # Perform remote append.
    updated = client.append([40, 50], db)

    # Display updated list.
    print("After RPC :", updated)

    # Stop the server.
    channel.request_queue.put(("client", b"STOP"))

    # Wait for server thread to finish.
    server_thread.join()


# Execute program.
if __name__ == "__main__":

    main()