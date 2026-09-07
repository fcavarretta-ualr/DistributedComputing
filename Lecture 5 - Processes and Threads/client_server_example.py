"""
Client/server example, using two separate processes that talk to
each other over a network connection -- a small pizzeria simulation.

- The SERVER process plays the role of the pizzeria: it listens for
  a connection, then waits for orders and replies to them.
- The CLIENT process plays the role of the customer: it connects to
  the pizzeria, places a couple of orders, and hangs up.

They run as two independent processes (each with its own memory), so
they cannot share Python variables directly -- everything they need
to tell each other has to travel over the connection as a message.

A multiprocessing.Queue is used only for LOGGING: both processes push
their status messages into it, and the main process reads from it and
prints them in the order they actually happened. Plain print() calls
from two different processes could otherwise interleave or get lost,
since each process has its own separate copy of standard output.
"""

import time

# multiprocessing.connection gives us Listener/Client, a simple way
# to open a socket-based connection between two processes and send
# whole Python objects back and forth with .send()/.recv().
from multiprocessing.connection import Listener, Client

# multiprocessing itself is needed for Process (to run the server and
# client concurrently) and Queue (to collect their log messages).
import multiprocessing


# The address the server listens on and the client connects to.
# ('localhost', 6000) means "port 6000 on this same machine" -- in a
# real distributed system the server's hostname/IP would go here
# instead, and the client could be running on a completely different
# computer.
ADDRESS = ('localhost', 6000)

# A simple shared secret so the client and server can confirm they're
# talking to each other and not some unrelated program on the same
# port. Listener/Client refuse to connect if this doesn't match.
AUTH_KEY = b'my_secret_password'


def run_server(log_queue):
    """Runs in the SERVER process: accepts one client and serves its orders."""
    log_queue.put("SERVER: Pizzeria is open for business!")

    # Listener opens a socket and waits for an incoming connection.
    # Using "with" makes sure the listening socket is closed
    # automatically once we're done with it.
    with Listener(ADDRESS, authkey=AUTH_KEY) as listener:
        log_queue.put(f"SERVER: Waiting for a customer to call at {ADDRESS}...")

        # .accept() blocks here until a client connects, then returns
        # a connection object we can send/recv messages through.
        with listener.accept() as conn:
            log_queue.put(f"SERVER: A customer connected! {listener.last_accepted}")

            while True:
                try:
                    # .recv() blocks until the client sends something.
                    msg = conn.recv()
                    log_queue.put(f"SERVER: Received order: '{msg}'")

                    if msg == 'order:pepperoni':
                        conn.send("Pizza:pepperoni is on its way!")
                    elif msg == 'order:margherita':
                        conn.send("Pizza:margherita is on its way!")
                    elif msg == 'hangup':
                        log_queue.put("SERVER: Customer hung up. Closing connection.")
                        break

                except EOFError:
                    # Raised if the client's connection drops without
                    # sending a proper 'hangup' message first.
                    log_queue.put("SERVER: Connection closed by client unexpectedly.")
                    break

    # Tell the main process this side is completely done.
    log_queue.put("DONE")


def run_client(log_queue):
    """Runs in the CLIENT process: connects to the server and places two orders."""
    log_queue.put("CLIENT: I'm hungry for pizza!")

    # Give the server a moment to start listening first. In a real
    # application you'd normally use a retry loop instead of a fixed
    # sleep, but this keeps the example simple.
    time.sleep(1)

    try:
        # Client() opens a connection to the server's address. The
        # authkey must match the one the server was created with.
        with Client(ADDRESS, authkey=AUTH_KEY) as conn:
            log_queue.put("CLIENT: Placing order: 'order:pepperoni'")
            conn.send('order:pepperoni')
            log_queue.put(f"CLIENT: Pizzeria response: '{conn.recv()}'")

            time.sleep(2)

            log_queue.put("CLIENT: Placing order: 'order:margherita'")
            conn.send('order:margherita')
            log_queue.put(f"CLIENT: Pizzeria response: '{conn.recv()}'")

            # Tell the server we're done, so it can close cleanly
            # instead of hitting the EOFError branch above.
            conn.send('hangup')
            log_queue.put("CLIENT: All done, hanging up.")

    except ConnectionRefusedError:
        # Happens if the client tries to connect before the server
        # is ready, or if the server isn't running at all.
        log_queue.put("CLIENT: Could not connect. Is the pizzeria open?")

    # Tell the main process this side is completely done.
    log_queue.put("DONE")


if __name__ == "__main__":
    # 1. Create a Queue that both child processes can share, used
    #    purely to funnel their log messages back to us in order.
    log_queue = multiprocessing.Queue()

    # 2. Create the server and client as two separate Process
    #    objects, each given the shared queue as an argument.
    #    Note the comma in args=(log_queue,) -- args always takes a
    #    tuple, and (log_queue) without the comma would just be
    #    log_queue itself, not a one-item tuple.
    server_process = multiprocessing.Process(target=run_server, args=(log_queue,))
    client_process = multiprocessing.Process(target=run_client, args=(log_queue,))

    # 3. Start both processes. From this point on the server and
    #    client are running concurrently and independently.
    server_process.start()
    client_process.start()

    # 4. Read from the queue and print each message as it arrives,
    #    until both the server and the client have signaled "DONE".
    done_count = 0
    while done_count < 2:
        # .get() blocks until a message is available in the queue.
        message = log_queue.get()
        if message == "DONE":
            done_count += 1
        else:
            print(message)

    # 5. .join() waits for both processes to fully terminate before
    #    the main process moves on -- otherwise the program could
    #    exit while a child process is still cleaning up.
    server_process.join()
    client_process.join()

    print("Main: Both client and server have finished.")
