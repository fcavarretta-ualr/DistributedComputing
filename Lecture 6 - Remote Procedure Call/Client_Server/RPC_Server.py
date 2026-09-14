# Import the RPyC library for remote procedure calls.
import rpyc

# Import ThreadedServer so that the server can handle client connections.
from rpyc.utils.server import ThreadedServer


# Define the server address.
SERVER = "localhost"

# Define the port number on which the server will listen.
PORT = 18861


# Create an RPC service by inheriting from rpyc.Service.
class DBListService(rpyc.Service):

    # This method runs whenever a client connects to the server.
    def on_connect(self, connection):

        # Create a separate list for the connected client.
        self.value = []

        # Display a message on the server when a client connects.
        print("A client has connected.")

    # This method runs whenever a client disconnects from the server.
    def on_disconnect(self, connection):

        # Display a message on the server when the client disconnects.
        print("A client has disconnected.")

    # The exposed_ prefix makes this method remotely callable.
    def exposed_append(self, data):

        # Add the received item to the server-side list.
        self.value.append(data)

        # Display the received value on the server.
        print(f"Appended value: {data}")

        # Return a copy of the updated list to the client.
        return list(self.value)

    # The exposed_ prefix makes this method remotely callable.
    def exposed_get_value(self):

        # Return a copy of the current server-side list.
        return list(self.value)


# Define the main function for starting the server.
def main():

    # Create a threaded RPyC server using DBListService.
    server = ThreadedServer(
        DBListService,

        # Specify the server address.
        hostname=SERVER,

        # Specify the server port.
        port=PORT,

        # Allow public attributes and exposed methods to be accessed.
        protocol_config={"allow_public_attrs": True}
    )

    # Display the server address before starting.
    print(f"RPC server is running on {SERVER}:{PORT}")

    # Display instructions for stopping the server.
    print("Press Ctrl+C to stop the server.")

    # Start the server and wait for client connections.
    server.start()


# Check whether this file is being run directly.
if __name__ == "__main__":

    # Start the server program.
    main()