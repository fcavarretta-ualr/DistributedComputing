'''
Note 4.8 - Implementing Stubs as global references
Shared constants (network addresses and operation codes)
'''

# ---------------------------------------------------------------------------
# Constants (Network addresses and operation codes)
# ---------------------------------------------------------------------------

# Address (host) and port number of the central server
HOSTS, PORTS = 'localhost', 6000

# Address and port for Client 1
HOSTC1, PORTC1 = 'localhost', 6001

# Address and port for Client 2
HOSTC2, PORTC2 = 'localhost', 6002

# Assign integer values to different operations
# CREATE   = 0
# APPEND   = 1
# GETVALUE = 2
# OK       = 3
CREATE, APPEND, GETVALUE, OK = range(4)

# Maximum number of bytes to receive at once
BUFSIZE = 4096
