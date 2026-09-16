import pickle          # Used to deserialize the DBClient object sent from Client 1 to Client 2 over the socket
import threading        # Provides Thread and Lock primitives for running the server and clients concurrently
import time              # Used for sleep() calls to give the server/clients time to start up before proceeding

# Import configuration constants: server host/port, and each client's own host/port
from config import HOSTS, PORTS, HOSTC2, PORTC2, PORTC1
from server import Server      # The Server class that listens for and handles remote list operations
from dbclient import DBClient  # Client-side proxy object used to talk to the remote list server (create/append/get)
from client import Client      # Low-level networking client used to send/receive raw data between Client 1 and 2

# Shared lock so print blocks don't interleave across threads
# This ensures that when multiple threads print multi-line status blocks,
# their output doesn't get mixed together on the console
print_lock = threading.Lock()


def client1():
    # Instantiate Client 1's low-level network client, bound to its own port
    c1 = Client(PORTC1)
    # Create a DBClient proxy for Client 1 to talk to the remote list server
    dbC1 = DBClient(HOSTS, PORTS)
    # Ask the server to create a new remote list and return its ID
    listID = dbC1.create()
    # Append the string 'Client 1' to the newly created remote list
    dbC1.appendData('Client 1')

    # Acquire the print lock so this status block prints atomically
    with print_lock:
        print(f"[Client 1]")                                         # Label this output block as coming from Client 1
        print(f"Created a new remote list on the server.")            # Confirm the list was created
        print(f"Assigned List ID: {listID}")                          # Show the ID assigned to the new list
        print(f"Added 'Client 1' to List # {listID}")                 # Confirm the append operation succeeded
        print(f"=====================================================")  # Visual separator

    # Serialize dbC1 (via Client's sendTo, which presumably pickles it) and send it to Client 2's host/port
    c1.sendTo(HOSTC2, PORTC2, dbC1)

    # Acquire the print lock again for the next status block
    with print_lock:
        print(f"[Client 1]")                                          # Label this output block as coming from Client 1
        print(f"Sent remote reference of List # 1 to Client 2")        # Confirm the reference was sent to Client 2
        print(f"=====================================================")  # Visual separator


def client2():
    # Instantiate Client 2's low-level network client, bound to its own port
    c2 = Client(PORTC2)
    # Block and wait to receive any incoming data (the pickled DBClient object from Client 1)
    data = c2.recvAny()
    # Deserialize the received bytes back into a DBClient object
    dbC2 = pickle.loads(data)
    # Append the string 'Client 2' to the same remote list referenced by dbC2
    dbC2.appendData('Client 2')

    # Acquire the print lock so this status block prints atomically
    with print_lock:
        print(f"[Client 2]")                                          
        print(f"Received List {dbC2.listID} from Client 1.")           
        print(f"Added 'Client 2' to the same remote list.")            
        print(f"=====================================================")  
        print(f"[Client2] Final list contents: {dbC2.getValue()}")     
        print(f"=====================================================")  


# Only run the following block if this script is executed directly (not imported as a module)
if __name__ == '__main__':
    server = Server()  # Create the server instance 
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()  # Start the server thread
    time.sleep(0.2)         # Pause briefly to give the server time to fully start up before clients connect

    # Start Client 2 in its own thread so it can listen for incoming data while Client 1 runs
    c2_thread = threading.Thread(target=client2)
    c2_thread.start()  
    time.sleep(0.2)     

    client1()           # Run Client 1's logic on the main thread (create list, append data, send reference to Client 2)
    c2_thread.join()    # Wait for Client 2's thread to finish before proceeding

    # Create a separate DBClient just to verify the final state of the list directly from the server
    verifier = DBClient(HOSTS, PORTS)
    verifier.listID = 1  # Manually set the list ID to 1 (assuming this was the first list created)
    # Acquire the print lock for the final verification output
    with print_lock:
        print(f"Server-side list #1: {verifier.getValue()}")  # Fetch and print the list's contents directly from the server, as a sanity check