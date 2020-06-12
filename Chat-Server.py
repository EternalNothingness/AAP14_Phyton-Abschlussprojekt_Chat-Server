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
    def __init__(self, host='localhost', port=12345, server_charset='cp850', n_listen=5):  # init variables with default values
        self.host = host    # define host
        self.port = port    # define port
        self.server_address = self.host, self.port # address consists of host and port
        self.server_charset = server_charset    # define character set

        self.n_listen = n_listen  # How often the server will allow unaccepted connections before refusing new ones
        self.n_client = 0   # number of active clients
        self.client_addresses = []    # memory for client addresses

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object

    # ------------------------- prepare_connection -------------------------
    def prepare_connection(self):
        self.s.bind(self.server_address)  # Bind to the port
        self.s.listen(self.n_listen)  # How often the server will allow unaccepted connections before refusing new ones
        # Server is now initialized and prepared for client connection

    # ------------------------- handle_connection -------------------------
    def handle_connection(self, conn, active_client_address):
        while True:
            try:
                data = conn.recv(1024)
                if data.decode(self.server_charset) == "":
                    break
                print("Got from client", active_client_address, ": %s" % data.decode(self.server_charset))
                for i in self.client_addresses:     # rotate in list
                    if i != active_client_address:
                        #should prevent sending data back to sender
                        print("Active Address:", active_client_address)
                        print("Client Address:", i)
                        print("Number of Clients:", self.n_client)
                        conn.sendto(data, i)  # send data to other chat participants
            except:
                print("Unexpected error:", sys.exc_info()[1])
                break
        conn.close()  # Close the connection
        self.n_client = self.n_client - 1
        self.client_addresses.remove(active_client_address)

    # ------------------------- establish_connection -------------------------
    def establish_connection(self):
        conn, active_client_address = self.s.accept()  # Establish connection with client.
        # return values: conn and address
        # 'conn' is a new socket object, which can be used to send and receive data on the connection
        # 'address' is the address of the socket on the other end of the connection
        print('Got connection from', active_client_address)

        self.n_client = self.n_client + 1
        self.client_addresses.append(active_client_address)  # storing the address of the client
        Thread(args=(conn, active_client_address), target=self.handle_connection).start()
        sleep(1)

########################### main program ###########################
oChat_Server = Chat_Server()
oChat_Server.prepare_connection()
while True:
    oChat_Server.establish_connection()
