# title: chat-server program
# authors: davidrieser & EternalNothingness
# created: 12.06.2020
# last change: 19.06.2020

########################### imports ###########################
import socket
import sys
from threading import Thread
from time import sleep

########################### classes ###########################
# ========================= Message ===========================
class Message(object):
    # ------------------------- init -------------------------
    def __init__(self):
        self.data = []  # list for data
        self.source_address = []    # list for source addresses
        self.n_message = -1   # number of messages - 1

    def add_data(self, data, source_address):
        self.data.append(data)
        self.source_address.append(source_address)
        self.n_message = self.n_message + 1

# ========================= Chat_Server =========================
class Chat_Server(object):

    # ------------------------- init -------------------------
    def __init__(self, host='localhost', port=12345, server_charset='cp850', n_listen=5):  # init variables with default values
        self.host = host    # define host
        self.port = port    # define port
        self.server_address = self.host, self.port # address consists of host and port
        self.server_charset = server_charset    # define character set

        self.n_listen = n_listen  # How often the server will allow unaccepted connections before refusing new ones
        self.client_addresses = []      # memory for client addresses
        self.client_usernames = []      # memory for client usernames
        self.client_ack = []            # memory for client status

        #if self.s is None: # If Socket isn't already initialized, initialize it
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object
        self.oMessage = Message()

    # ------------------------- prepare_connection -------------------------
    def prepare_connection(self):
        self.s.bind(self.server_address)  # Bind to the port
        self.s.listen(self.n_listen)  # How often the server will allow unaccepted connections before refusing new ones
        # Server is now initialized and prepared for client connection

    # ------------------------- establish_connection -------------------------
    def establish_connection(self):
        conn, active_client_address = self.s.accept()  # Establish connection with client.
        # return values: conn and address
        # 'conn' is a new socket object, which can be used to send and receive data on the connection
        # 'address' is the address of the socket on the other end of the connection
        print('got connection from', active_client_address)

        Thread(args=(conn, active_client_address), target=self.handle_connection_in).start()
        sleep(1)

    # ------------------------- handle_connection_in -------------------------
    def handle_connection_in(self, conn, active_client_address):
        active_client_username = ""
        username_ack = ""
        while True:
            try:
                if (username_ack == "") | (username_ack == "n_ack"):
                    data = conn.recv(1024)
                    data_decode = data.decode(self.server_charset)
                    active_client_username = data_decode[0:9]  # max. name length: 10
                    print("new username:", active_client_username)
                    looped = False
                    for i in self.client_usernames:     # prevents that several users would get the same name
                        looped = True
                        print("existing username:", i)
                        if i == active_client_username:
                            username_ack = "n_ack"
                            print(username_ack)
                            conn.sendall(username_ack.encode(self.server_charset))
                            break
                        username_ack = "ack_add"
                    if not looped:
                        username_ack = "ack_add"
                elif username_ack == "ack_add":
                    username_ack = "ack"
                    print(username_ack)
                    self.client_addresses.append(active_client_address)     # storing the address of the client
                    self.client_usernames.append(active_client_username)    # storing the name of the user
                    self.client_ack.append(username_ack)                    # storing the status of the client
                    self.oMessage.add_data("=> User <"+ active_client_username +"> logged in",active_client_address)
                    print("list of users:", self.client_usernames)
                    print("list of addresses:", self.client_addresses)
                    print("list of stats:", self.client_ack)
                    conn.sendall(username_ack.encode((self.server_charset)))
                    Thread(args=(conn, active_client_address), target=self.handle_connection_out).start()
                elif username_ack == "ack":
                    if self.client_ack[self.client_addresses.index(active_client_address)] == "closed":
                        break
                    if "closed" in self.client_ack: # should avoid real-time problems (threading + closing of conns)
                        sleep(1)
                    data = conn.recv(1024)
                    if (not data) | (len(data) == 0) | (data == ""):
                        print("=> EOF was sent, closing socket")
                        conn.sendall("".encode(self.server_charset))
                        break
                    data_decode = data.decode(self.server_charset)
                    if data_decode == "":
                        print("=> EOF was sent, closing socket")
                        break
                    print("received data from:", active_client_address, ": %s" % data_decode)
                    self.oMessage.add_data(data_decode, active_client_address)
            except:
                print("Connection was closed on the Client Side") #, sys.exc_info()[1])
                break

        # Finalizer

        self.oMessage.add_data("=> User <" + active_client_username + "> logged out",active_client_address)

        conn.close()  # Close the connection
        if (username_ack == "ack") | (active_client_address in self.client_addresses):
            # Cannot be done here => handle_connection_out will throw Error
                # self.client_addresses.remove(active_client_address)
                # self.client_ack[self.client_addresses.index(active_client_address)] = "closed"
            self.client_usernames.remove(active_client_username)

    # ------------------------- handle_connection_out -------------------------
    def handle_connection_out(self, conn, active_client_address):
        active_client_username = self.client_usernames[self.client_addresses.index(active_client_address)]
        n_message = self.oMessage.n_message
        while True:
            try:
                if self.client_ack[self.client_addresses.index(active_client_address)] == "closed":
                    if active_client_address in self.client_addresses:
                        self.client_addresses.remove(active_client_address)
                        self.client_ack[self.client_addresses.index(active_client_address)] = "closed"
                    break
                if "closed" in self.client_ack: # should avoid real-time problems (threading + closing of conns)
                    sleep(1)
                if self.oMessage.n_message > n_message:
                    n_message = n_message + 1
                    if self.oMessage.source_address[n_message] != active_client_address:
                        print("sending data to:", active_client_address)
                        data = self.client_usernames[self.client_addresses.index(self.oMessage.source_address[n_message])] + " said: " + self.oMessage.data[n_message]
                        conn.sendall(data.encode(self.server_charset))
            except:
                print("Connection was closed on the Client Side") #, sys.exc_info()[1])
                break

########################### main program ###########################
if __name__ == "__main__":
    oChat_Server = Chat_Server()
    oChat_Server.prepare_connection()
    while True:
        oChat_Server.establish_connection()
