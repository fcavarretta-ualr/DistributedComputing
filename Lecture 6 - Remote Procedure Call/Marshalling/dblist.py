"""
===========================================================================================
Fig-4.9-Example- A simple RPC example for operation append with proper marshaling.
===========================================================================================
dblist.py — DATA LAYER

Represents the "database" that the RPC operates on. Wraps a Python list
with an append() method and a readable repr. Unchanged between the plain
and marshalled versions of this example — the data itself doesn't know or
care whether it's being transmitted across a network.
"""


# Database list stored on the server.
class DBList:

    # Constructor to initialize the database list.
    def __init__(self, initial_values=None):

        # Create an internal list.
        self.value = list(initial_values) if initial_values else []

    # Append new data to the database list.
    def append(self, data):

        # Add all elements from data to the list.
        self.value.extend(data)

        # Return the updated object.
        return self

    # Define how the object is displayed.
    def __repr__(self):

        # Return the object in readable form.
        return f"DBList({self.value})"
