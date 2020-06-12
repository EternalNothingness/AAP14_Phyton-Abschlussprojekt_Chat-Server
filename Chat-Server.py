# title: chat-server program
# author: EternalNothingness
# created: 12.06.2020
# last change: 12.06.2020

########################### imports ###########################
import socket
import sys
from threading import Thread
from time import sleep

########################### classes ###########################
class Chat_Server(object):

    # ------------------------- init -------------------------
    def __init__(self, host='localhost', port=12345, server_charset='cp850', n=5):  # init variables with default values
        self.host = host    # define host
        self.port = port    # define port
        self.address = self.host, self.port # address consists of host and port
        self.server_charset = server_charset    # define character set
        self.n = n  # How often the server will allow unaccepted connections before refusing new ones
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object

    # ------------------------- prepare_connection -------------------------
    def prepare_connection(self):
        self.s.bind(self.address)  # Bind to the port
        self.s.listen(self.n)  # How often the server will allow unaccepted connections before refusing new ones
        # Server is now initialized and prepared for client connection

    # ------------------------- handle_connection -------------------------
    def handle_connection(self, c, src):
        while True:
            try:
                data = c.recv(1024)
                if data.decode(self.server_charset) == "":
                    break
                print("Got from client", src, ": %s" % data.decode(self.server_charset))
                c.send(data)  # send data back
            except:
                print("Unexpected error:", sys.exc_info()[1])
                break
        c.close()  # Close the connection

    # ------------------------- establish_connection -------------------------
    def establish_connection(self):
        conn, client_address = self.s.accept()  # Establish connection with client.
        # return values: conn and address
        # 'conn' is a new socket object, which can be used to send and receive data on the connection
        # 'address' is the address of the socket on the other end of the connection
        print('Got connection from', client_address)
        Thread(args=(conn, client_address), target=self.handle_connection).start()
        sleep(1)

########################### main program ###########################
oChat_Server = Chat_Server()
oChat_Server.prepare_connection()
while True:
    oChat_Server.establish_connection()
