'''
Note 4.8 - Implementing Stubs as global references
Figure 4.20 (a) - DBClient (Client Stub)
'''

# Import the socket module for network communication (TCP/IP sockets)
import socket

# Import pickle to serialize (convert objects to bytes) and deserialize them
import pickle

# Import shared constants
from config import CREATE, APPEND, GETVALUE, BUFSIZE


# ---------------------------------------------------------------------------
# Figure 4.20 (a) - DBClient (Client Stub)
# ---------------------------------------------------------------------------
class DBClient:

    # Constructor
    def __init__(self, host, port):

        # Store server hostname
        self.host = host

        # Store server port
        self.port = port

        # Initially no list has been created
        self.listID = None

    # Private helper function used by every RPC
    def __sendrecv(self, message):

        # Create TCP socket
        sock = socket.socket(socket.AF_INET,
                             socket.SOCK_STREAM)

        # Connect to server
        sock.connect((self.host, self.port))

        # Serialize and send request
        sock.send(pickle.dumps(message))

        # Receive server response
        result = pickle.loads(sock.recv(BUFSIZE))

        # Close connection
        sock.close()

        # Return response
        return result

    # Create a new remote list
    def create(self):

        # Ask server to create a list
        self.listID = self.__sendrecv([CREATE])

        # Return assigned list ID
        return self.listID

    # Read remote list
    def getValue(self):

        # Request server to return list contents
        return self.__sendrecv([GETVALUE,
                                self.listID])

    # Append data into remote list
    def appendData(self, data):

        # Request server to append item
        return self.__sendrecv([APPEND,
                                data,
                                self.listID])
