'''
Note 4.7 - Figure 4.9- Example: A simple socket-based client-server system

'''

from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, socket

HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 1024


class Server:
    def run(self) -> None:
        """Start the server and communicate with one client."""

        # Create an IPv4 TCP socket.
        with socket(AF_INET, SOCK_STREAM) as server_socket:
            # Allow the address to be reused after restarting the program.
            server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

            # Attach the server socket to the IP address and port.
            server_socket.bind((HOST, PORT))

            # Start listening for client connections.
            server_socket.listen(1)

            print(f"Server is listening on {HOST}:{PORT}...")

            # Wait until a client connects.
            conn, addr = server_socket.accept()

            # Automatically close the client connection when finished.
            with conn:
                print(f"Connected by client: {addr}")

                while True:
                    # Receive up to 1024 bytes from the client.
                    data = conn.recv(BUFFER_SIZE)

                    # An empty byte string means the client closed the connection.
                    if not data:
                        print("Client closed the connection.")
                        break

                    print(f"Received: {data.decode('utf-8')}")

                    # Add an asterisk and send the message back.
                    response = data + b"*"
                    conn.sendall(response)

                    print(f"Sent: {response.decode('utf-8')}")

        print("Server stopped.")


if __name__ == "__main__":
    server = Server()
    server.run()