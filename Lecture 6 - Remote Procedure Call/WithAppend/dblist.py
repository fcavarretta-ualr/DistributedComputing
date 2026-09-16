"""
===========================================================
Fig-4.8-Example- A simple RPC example for operation append.
===========================================================

dblist.py — DATA LAYER

Represents the "database" that the RPC operates on. In a real system this
would be a table in Postgres, a MongoDB collection, or similar. Here it's
just a wrapper around a Python list so the RPC mechanics stay the focus.
"""


# Define a class that represents a database list stored on the server.
class DBList:

    # Constructor to initialize the database list.
    def __init__(self, initial_values=None):

        # Create the internal list. If initial values exist, copy them;
        # otherwise create an empty list.
        self.value = list(initial_values) if initial_values else []

    # Method to append data into the database list.
    def append(self, data):

        # Add all elements from 'data' into the internal list.
        self.value.extend(data)

        # Return the updated object.
        return self

    # Define how the object will be displayed when printed.
    def __repr__(self):

        # Return the list in a readable format.
        return f"DBList({self.value})"
