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
class Message(object):
    def __init__(self,thread_id=0,message_text=""):
        self.thread_id = thread_id
        self.message_text = message_text
        self.read_by_threads = [] # Remember all Threads this message was read by

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
        
        self.messages = [] # Remember all Messages which where sent to the Server

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object

    # ------------------------- prepare_connection -------------------------
    def prepare_connection(self):
        self.s.bind(self.server_address)  # Bind to the port
        self.s.listen(self.n_listen)  # How often the server will allow unaccepted connections before refusing new ones
        # Server is now initialized and prepared for client connection

    # ------------------------- handle_connection -------------------------
    def handle_connection(self, conn, active_client_address,thread_id):
        while True:
            try:
                data = conn.recv(1024)
                if data.decode(self.server_charset) == "":
                    break
                message_text = data.decode(self.server_charset)
                print("Got from client ", active_client_address, " on Thread " , thread_id , ": %s" % message_text)
                self.messages.append(Message(thread_id,message_text))
                
                # Check if all Messages the Server has received were also sent to all the Clients
                for m in self.messages:
                    if(thread_id not in m.read_by_threads):
                        m.read_by_threads.append(thread_id)
                        #TODO Change to sendAll
                        conn.sendto(m.message_text, active_client_address)
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
        Thread(args=(conn, active_client_address,self.n_client), target=self.handle_connection).start()
        sleep(1)

########################### main program ###########################
oChat_Server = Chat_Server()
oChat_Server.prepare_connection()
while True:
    oChat_Server.establish_connection()
