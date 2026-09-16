'''
Note 4.8 - Implementing Stubs as global references
Figure 4.20 (c) - Client
'''

# Import the socket module for network communication (TCP/IP sockets)
import socket

# Import pickle to serialize (convert objects to bytes) and deserialize them
import pickle

# Import shared constants
from config import BUFSIZE


# ---------------------------------------------------------------------------
# Figure 4.20 (c) - Client
# ---------------------------------------------------------------------------
class Client:

    # Constructor
    def __init__(self, port):

        # Localhost
        self.host = 'localhost'

        # Store listening port
        self.port = port

        # Create TCP socket
        self.sock = socket.socket(socket.AF_INET,
                                  socket.SOCK_STREAM)

        # Allow quick port reuse
        self.sock.setsockopt(socket.SOL_SOCKET,
                             socket.SO_REUSEADDR,
                             1)

        # Bind socket
        self.sock.bind((self.host,
                        self.port))

        # Start listening
        self.sock.listen(2)

    # Send any Python object to another client
    def sendTo(self,
               host,
               port,
               data):

        # Create temporary socket
        sock = socket.socket(socket.AF_INET,
                             socket.SOCK_STREAM)

        # Connect to destination client
        sock.connect((host,
                      port))

        # Serialize and send object
        sock.send(pickle.dumps(data))

        # Close connection
        sock.close()

    # Wait until another client sends data
    def recvAny(self):

        # Block until connection arrives
        conn, addr = self.sock.accept()

        # Receive bytes
        data = conn.recv(BUFSIZE)

        # Close connection
        conn.close()

        # Return received bytes
        return data
