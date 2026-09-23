'''
Example of Message queuing model Using POLL function (bounded polling)
'''

import queue        # thread-safe FIFO queue
import threading    # for running sender/receiver concurrently
import time          # for sleep/delays

message_queue = queue.Queue()   # shared queue between sender and receiver


# -------------------- Sender --------------------
def sender():
    time.sleep(5)                              # simulate delay before message is ready
    message_queue.put("Hello from Sender!")     # push message into the queue
    print("[Sender] Message sent.")              # log confirmation


# -------------------- Receiver (Polling) --------------------
def receiver(max_iterations=8):        # <-- enough polls to outlast the 5s send delay

    # Poll at most max_iterations times
    for _ in range(max_iterations):     # loop up to max_iterations times

        if not message_queue.empty():   # check if a message has arrived
            message = message_queue.get()          # retrieve the message
            print("[Receiver] Received:", message)  # log received message
            break                      # got it -> skip the else

        else:
            print("[Receiver] No message available. Checking again...")  # log miss
            time.sleep(1)               # wait before polling again

    else:
        # Runs ONLY if the loop finished without break
        print("[Receiver] No message received.")   # log timeout/failure


threading.Thread(target=sender).start()     # start sender thread
threading.Thread(target=receiver).start()   # start receiver thread