"""
Multiprocessing example.

Goal: run the same worker function twice, each time in its own
separate PROCESS, and see that they run concurrently.

A process is an independent instance of a running program, with its
own private memory space -- two processes cannot see each other's
variables directly. This is different from a thread (see
multithreading_example.py), where multiple threads share the same
memory space within one process.
"""

# The multiprocessing module lets us create and manage new processes
# from within a Python program.
import multiprocessing

# time.sleep() is used here only to simulate a long-running task
# (e.g. a heavy calculation, or waiting on a slow resource).
import time


def worker_function(name):
    """The function each child process will run."""
    print(f"Process {name}: Starting...")

    # Pausing for 2 seconds stands in for real CPU-bound work, such
    # as a complex calculation, processing a large file, or waiting
    # on a network request.
    time.sleep(2)

    print(f"Process {name}: Finished.")


# This guard ensures the code below only runs when this file is
# executed directly (the "main" program), not when it gets imported.
# On some platforms, multiprocessing re-imports this file inside each
# child process to set it up -- without this guard, that re-import
# would try to spawn a whole new set of child processes itself,
# causing an infinite loop of process creation.
if __name__ == "__main__":
    print("Main process: Starting worker processes...")

    # Create two Process objects. Each one is a separate, independent
    # process that will run worker_function() with its own arguments.
    # Note: creating a Process object does not start it running yet.
    process1 = multiprocessing.Process(target=worker_function, args=("Worker 1",))
    process2 = multiprocessing.Process(target=worker_function, args=("Worker 2",))

    # .start() actually launches each process. Because both are
    # started before either is waited on, they run concurrently: the
    # 2-second sleep() calls overlap instead of adding up to 4 seconds.
    process1.start()
    process2.start()

    # .join() is a synchronization point: it tells the main process
    # "pause here and wait until this child process has completely
    # finished running."
    process1.join()
    process2.join()

    # This line only runs after BOTH join() calls have returned,
    # meaning both child processes have fully finished.
    print("Main process: All worker processes finished.")
