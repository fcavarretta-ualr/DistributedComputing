"""
===========================================================================================
Fig-4.9-Example- A simple RPC example for operation append with proper marshaling.
===========================================================================================

main.py — ENTRY POINT

Wires everything together:
  - Creates the shared Channel
  - Starts the Server in a background thread
  - Creates a Client and a DBList
  - Demonstrates one marshalled RPC call, then sends STOP to shut the
    server down

Run with:
    python main.py
"""


# Import threading module to run the server in a separate thread.
import threading

# Import the four building blocks from their own modules.
from channel import Channel
from client import Client
from dblist import DBList
from server import Server


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

    # Perform remote append (marshalled under the hood).
    updated = client.append([40, 50], db)

    # Display updated list.
    print("After RPC :", updated)

    # Stop the server — sent as raw bytes so the server can shortcut
    # the unmarshalling step.
    channel.request_queue.put(("client", b"STOP"))

    # Wait for server thread to finish.
    server_thread.join()


# Execute program.
if __name__ == "__main__":

    main()
