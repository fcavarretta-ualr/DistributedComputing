"""
Multithreading example.

Goal: run the same worker function twice, each time in its own
separate THREAD, and see that they run concurrently.

A thread is a sequence of instructions that runs within a process.
Unlike separate processes, all the threads of one process share that
process's memory space -- they can see and modify the same
variables. This is the mirror image of multiprocessing_example.py,
where each worker ran in its own isolated process instead.
"""

# The threading module lets us create and manage new threads from
# within a Python program.
import threading

# time.sleep() is used here only to simulate a long-running task
# (e.g. waiting on a network request or a slow disk read).
import time


def worker_function(name):
    """The function each thread will run."""
    print(f"Thread {name}: Starting...")

    # Pausing for 2 seconds stands in for a task that spends most of
    # its time waiting rather than computing, such as a network
    # request or file I/O -- a good fit for threads, since a blocked
    # thread doesn't stop the other threads in the same process from
    # making progress.
    time.sleep(2)

    print(f"Thread {name}: Finished.")


# This guard ensures the code below only runs when this file is
# executed directly (the "main" program), not when it gets imported.
if __name__ == "__main__":
    print("Main thread: Starting worker threads...")

    # Create two Thread objects. Each one will run worker_function()
    # with its own arguments. Creating a Thread object does not start
    # it running yet -- that happens with .start() below.
    thread1 = threading.Thread(target=worker_function, args=("Worker 1",))
    thread2 = threading.Thread(target=worker_function, args=("Worker 2",))

    # .start() actually launches each thread. Because both are started
    # before either is waited on, they run concurrently: the two
    # 2-second sleep() calls overlap instead of adding up to 4 seconds.
    thread1.start()
    thread2.start()

    # .join() is a synchronization point: it tells the main thread
    # "pause here and wait until this other thread has completely
    # finished running."
    thread1.join()
    thread2.join()

    # This line only runs after BOTH join() calls have returned,
    # meaning both worker threads have fully finished.
    print("Main thread: All worker threads finished.")
