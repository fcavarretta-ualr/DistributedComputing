# Import the RPyC library for connecting to the RPC server.
import rpyc


# Define the server address.
SERVER = "localhost"

# Define the port number used by the server.
PORT = 18861


# Create the client class.
class Client:

    # Define the method that performs the client operations.
    def run(self):

        # Initialize the connection variable.
        connection = None

        # Begin error handling.
        try:

            # Connect to the RPC server.
            connection = rpyc.connect(SERVER, PORT)

            # Display a successful connection message.
            print("Connected to the RPC server.")

            # Remotely call append and add 2 to the server-side list.
            first_result = connection.root.append(2)

            # Display the list returned after the first remote call.
            print("After appending 2:", first_result)

            # Remotely call append and add 4 to the server-side list.
            second_result = connection.root.append(4)

            # Display the list returned after the second remote call.
            print("After appending 4:", second_result)

            # Remotely request the complete current list.
            final_result = connection.root.get_value()

            # Print the current list stored by the server.
            print("Final server list:", final_result)

        # Handle errors such as the server not running.
        except ConnectionRefusedError:

            # Inform the user that the client could not reach the server.
            print("Connection failed. Start rpc_server.py first.")

        # Handle other possible errors.
        except Exception as error:

            # Display the unexpected error.
            print(f"An error occurred: {error}")

        # Run this block whether an error occurs or not.
        finally:

            # Check whether a connection was successfully created.
            if connection is not None:

                # Close the client-server connection.
                connection.close()

                # Display a connection-closed message.
                print("Connection closed.")


# Define the main function.
def main():

    # Create a Client object.
    client = Client()

    # Run the client's RPC operations.
    client.run()


# Check whether this file is being executed directly.
if __name__ == "__main__":

    # Start the client program.
    main()