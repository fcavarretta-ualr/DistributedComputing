'''
Note 4.8 - Implementing Stubs as global references
Figure 4.20 (b) - Server
'''

# Import the socket module for network communication (TCP/IP sockets)
import socket

# Import pickle to serialize (convert objects to bytes) and deserialize them
import pickle

# Import shared constants
from config import HOSTS, PORTS, CREATE, APPEND, GETVALUE, OK, BUFSIZE


# ---------------------------------------------------------------------------
# Figure 4.20 (b) - Server
# ---------------------------------------------------------------------------
class Server:

    # Constructor executed whenever a Server object is created
    def __init__(self, host=HOSTS, port=PORTS):

        # Dictionary that stores all lists.
        # Example:
        # {1:['A','B'], 2:['X','Y']}
        self.setOfLists = {}

        # Store server hostname
        self.host = host

        # Store server port number
        self.port = port

        # Create a TCP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Allow reuse of the same port after restarting the program
        self.sock.setsockopt(socket.SOL_SOCKET,
                             socket.SO_REUSEADDR,
                             1)

        # Bind the socket to the host and port
        self.sock.bind((self.host, self.port))

        # Begin listening for incoming client connections
        self.sock.listen(5)

    # Continuously wait for client requests
    def run(self):

        # Infinite server loop
        while True:

            # Wait until a client connects
            conn, addr = self.sock.accept()

            # Receive bytes sent by the client
            data = conn.recv(BUFSIZE)

            # If nothing was received, close connection
            if not data:
                conn.close()
                continue

            # Convert received bytes back into a Python object
            request = pickle.loads(data)

            # -------------------------
            # CREATE Operation
            # -------------------------
            if request[0] == CREATE:

                # Generate a new list ID
                listID = len(self.setOfLists) + 1

                # Create an empty list
                self.setOfLists[listID] = []

                # Send the newly created list ID back to client
                conn.send(pickle.dumps(listID))

            # -------------------------
            # APPEND Operation
            # -------------------------
            elif request[0] == APPEND:

                # Extract list ID from request
                listID = request[2]

                # Extract item to append
                item = request[1]

                # Append item into the server's list
                self.setOfLists[listID].append(item)

                # Send OK response
                conn.send(pickle.dumps(OK))

            # -------------------------
            # GETVALUE Operation
            # -------------------------
            elif request[0] == GETVALUE:

                # Extract list ID
                listID = request[1]

                # Retrieve requested list
                result = self.setOfLists[listID]

                # Send list back to client
                conn.send(pickle.dumps(result))

            # Close client connection
            conn.close()
