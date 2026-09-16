"""
===========================================================
Fig-4.8-Example- A simple RPC example for operation append.
===========================================================

main.py — ENTRY POINT

Wires everything together:
  - Creates the shared Channel
  - Starts the Server in a background thread
  - Creates a Client and a DBList
  - Demonstrates one RPC call, then sends STOP to shut the server down

Run with:
    python main.py
"""


# Import threading to run the server and client simultaneously.
import threading

# Import the four building blocks from their own modules.
from channel import Channel
from client import Client
from dblist import DBList
from server import Server


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
