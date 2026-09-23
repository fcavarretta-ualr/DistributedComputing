'''
MessageQueueWithBroker
Sender → Input Queue → Message Broker → Output Queue → Receiver
'''

from queue import Queue
import threading
import time

# Two queues
input_queue = Queue()
output_queue = Queue()


# Sender application
def sender():
    message = "john|25|USA"

    print("Sender sent:", message)

    # PUT message into the input queue
    input_queue.put(message)


# Message broker
def broker():
    # GET message from the input queue
    message = input_queue.get()

    print("Broker received:", message)

    # Convert the message format
    name, age, country = message.split("|")

    converted_message = {
        "name": name,
        "age": age,
        "country": country
    }

    print("Broker converted:", converted_message)

    # PUT converted message into the output queue
    output_queue.put(converted_message)


# Receiver application
def receiver():
    # GET converted message from the output queue
    message = output_queue.get()

    print("Receiver received:", message)


# Create threads
sender_thread = threading.Thread(target=sender)
broker_thread = threading.Thread(target=broker)
receiver_thread = threading.Thread(target=receiver)

# Start receiver and broker first
receiver_thread.start()
broker_thread.start()

time.sleep(1)

# Start sender
sender_thread.start()

# Wait for all threads
sender_thread.join()
broker_thread.join()
receiver_thread.join()

print("Communication completed.")