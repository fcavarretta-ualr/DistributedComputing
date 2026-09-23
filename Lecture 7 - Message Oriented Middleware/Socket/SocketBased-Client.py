'''
Note 4.7 - Figure 4.9- Example: A simple socket-based client-server system
'''


from socket import AF_INET, SOCK_STREAM, socket

HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 1024


class Client:
    def run(self) -> None:
        """Connect to the server, send a message, and receive a response."""

        # Create an IPv4 TCP socket.
        with socket(AF_INET, SOCK_STREAM) as client_socket:
            print(f"Connecting to server at {HOST}:{PORT}...")

            # Connect to the server.
            client_socket.connect((HOST, PORT))

            message = "Hello, world"

            # Convert the string into bytes and send it.
            client_socket.sendall(message.encode("utf-8"))
            print(f"Sent: {message}")

            # Wait for the server's response.
            data = client_socket.recv(BUFFER_SIZE)

            if data:
                print(f"Received: {data.decode('utf-8')}")
            else:
                print("The server closed the connection without responding.")

        # Leaving the with block closes the socket.
        print("Client connection closed.")


if __name__ == "__main__":
    client = Client()
    client.run()