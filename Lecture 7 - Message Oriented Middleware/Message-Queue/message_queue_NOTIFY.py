'''
Example of Message queuing model Using NOTIFY function

'''



import queue              # Provides the Queue class
import threading          # Used for multithreading
import time               # Used for delay

# Create a message queue
message_queue = queue.Queue()

# Create an Event object for notification
message_event = threading.Event()


# -------------------- Sender --------------------
def sender():

    # Wait for 5 seconds
    time.sleep(5)

    # Put a message into the queue
    message_queue.put("Hello from Sender!")

    # Display confirmation
    print("[Sender] Message sent.")

    # Notify the receiver that a message is ready
    message_event.set()


# -------------------- Receiver --------------------
def receiver():

    # Inform the user that the receiver is waiting
    print("[Receiver] Waiting for a message...")

    # Wait until the sender sends a notification
    message_event.wait()

    # Retrieve the message from the queue
    message = message_queue.get()

    # Display the received message
    print("[Receiver] Received:", message)


# Create and start the sender thread
threading.Thread(target=sender).start()

# Create and start the receiver thread
threading.Thread(target=receiver).start()