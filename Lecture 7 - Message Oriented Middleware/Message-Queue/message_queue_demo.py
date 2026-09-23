'''
Example of Message queuing model Using PUT and GET functions

'''

from queue import Queue
import threading
import time

# Create a message queue
message_queue = Queue()


# Sender (Producer)
def sender():
    messages = ["Hello", "How are you?", "Goodbye"]

    for msg in messages:
        print("-" * 50)
        print(f"Sender: Sending -> {msg}")
        

        # PUT operation
        message_queue.put(msg)
        time.sleep(1)

    # Send STOP message
    print("-" * 50)
    print("Sender: Sending -> STOP")
    

    message_queue.put("STOP")


# Receiver (Consumer)
def receiver():
    while True:
        print("-" * 50)
        print("Receiver: Waiting for message...")
       

        # GET operation (blocks if queue is empty)
        msg = message_queue.get()

        if msg == "STOP":
            print("-" * 50)
            print("Receiver: Communication Finished")
            
            break

        print("-" * 50)
        print(f"Receiver: Received -> {msg}")
        

        time.sleep(2)


# Create threads
t1 = threading.Thread(target=sender)
t2 = threading.Thread(target=receiver)

# Start Receiver first
t2.start()

# Delay sender to show receiver is waiting
time.sleep(3)

# Start Sender
t1.start()

# Wait for both threads to finish
t1.join()
t2.join()

print("-" * 50)
print("Program Finished")
print("-" * 50)
