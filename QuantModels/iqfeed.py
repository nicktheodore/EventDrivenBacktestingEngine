
# coding: utf-8

# In[1]:

# iqfeed.py


# In[2]:

import sys
import socket


# In[3]:

def read_historical_data_socket(sock, recv_buffer=4096):
    """
    Read the information from the socket, in a buffered fashion, receiving only 4096 bytes at a time.
    
    Parameters:
    sock - The socket object
    recv_buffer - Amount in bytes to receive per read
    """
    buffer = ""
    data = ""
    while True:
        data = sock.recv(recv_buffer)
        buffer += data
        
        # Check if the end message string arrives
        if "!ENDMSG!" in buffer:
            break
    # Remove the end message string
    buffer = buffer[:-12]
    return buffer


# In[6]:

if __name__ == "__main__":
    # Define server host, port, and symbols to download
    host = "127.0.0.1" # Localhost
    port = 9100 # Historical data socket port
    syms = ["SPY", "IWM"]
    
    # Download each symbol to disk
    for sym in syms:
        print("Downloading symbol: %s..." % sym)
        
    # Construct the message needed by IQFeed to retrieve data
    message = "HIT,%s,60,20070101 075000,,,093000,160000,1\n" % sym
    
    # Open a streaming socket to the IQFeed server locally
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    
    # Send the historical data request message and the buffer data
    sock.sendall(message)
    data = read_historical_data_socket(sock)
    sock.close
    
    # Remove all the endlines and the line-ending comma delimiter from each record
    data = "".join(data.split("\r"))
    data = data.replace(",\n", "\n")[:-1]
    
    # Write the data stream to disk
    f = open("%s.csv" % sym, "w")
    f.write(data)
    f.close()


# In[ ]:



