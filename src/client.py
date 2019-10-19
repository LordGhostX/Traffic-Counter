# client.py

import socket
import sys
import time

# setup the script
TCP_PORT = 10000
AVERAGE_FPS = 20

def do_something(number_of_vehicles):
    pass

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Created connection socket")

# Connect the socket to the port where the server is listening
server_address = ("localhost", 10000)
sock.connect(server_address)
print("Connected to {} on port {}".format(*server_address))

if len(sys.argv) > 1:
    sock.sendall(sys.argv[1].encode('utf-8'))
else:
    try:
        while True:
            # Send data
            message = "count vehicles"
            sock.sendall(message.encode('utf-8'))

            data = sock.recv(4096).decode()
            if len(data) > 0:
                print("Detected {} vehicles".format(data))
                do_something(int(data))
            else:
                print("No data received from the server")
                break

            # sleep for a while
            #time.sleep(1 / 1000 / AVERAGE_FPS)
    except Exception as e:
        print(e)
        pass

    finally:
        print("Closing the connection socket")
        sock.sendall("close server".encode('utf-8'))
        sock.close()
        exit()

print("Exited the client")
