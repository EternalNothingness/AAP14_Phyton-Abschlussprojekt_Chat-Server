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
# * database for incoming messages
class Message(object):
    # ------------------------- init -------------------------
    def __init__(self):
        self.data = []  # list for data
        self.source_address = []    # list for source addresses
        self.source_username = []   # list for source usernames
        self.n_message = -1   # index number of latest message

    # ------------------------- add_data -------------------------
    # * adds data (message, source address, source username) to the database
    # * increments n_message
    def add_data(self, data, source_address, source_username):
        self.data.append(data)
        self.source_address.append(source_address)
        self.source_username.append(source_username)
        self.n_message = self.n_message + 1

# ========================= Chat_Server =========================
class Chat_Server(object):

    # ------------------------- init -------------------------
    def __init__(self, host='localhost', port=12345, server_charset='cp850', n_listen=5):
        self.host = host    # define host
        self.port = port    # define port
        self.server_address = self.host, self.port # address consists of host and port
        self.server_charset = server_charset    # define character set

        self.n_listen = n_listen  # How often the server will allow unaccepted connections before refusing new ones
        self.client_addresses = []      # list for client addresses
        self.client_usernames = []      # list for client usernames
        self.client_ack = []            # list for client status
        self.SYSTEM = "SYSTEM"          # variable for system messages

        #if self.s is None: # If Socket isn't already initialized, initialize it
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object
        self.oMessage = Message()   # message object, database for messages

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

        Thread(args=(conn, active_client_address), target=self.handle_connection_in).start()    # starts Thread for
        # handle_in-method
        sleep(0.1)

    # ------------------------- handle_connection_in -------------------------
    # handles input and stores it in database
    def handle_connection_in(self, conn, active_client_address):
        active_client_username = ""     # variable for the username of this connection
        username_ack = ""               # variable needed for the allocation of the username
        while True:
            try:
                # ------------------------- username allocation -------------------------
                if (username_ack == "") | (username_ack == "n_ack"):    # if yes => username not set
                    data = conn.recv(1024)
                    data_decode = data.decode(self.server_charset)
                    active_client_username = data_decode[0:9]  # max. name length: 10
                    print("new username:", active_client_username)
                    looped = False
                    for i in self.client_usernames:     # prevents that several users would get the same name
                        looped = True
                        print("existing username:", i)
                        if i == active_client_username:
                            username_ack = "n_ack"      # username already used
                            print(username_ack)
                            conn.sendall(username_ack.encode(self.server_charset))  # returns username_ack to client
                            break
                        username_ack = "ack_add"    # username not used and will be added
                    if not looped:      # no entry in list => first user
                        username_ack = "ack_add"
                    if active_client_username == self.SYSTEM:   # no user should have the same label as the system
                        username_ack = "n_ack"
                        print(username_ack)
                        conn.sendall(username_ack.encode(self.server_charset))
                elif username_ack == "ack_add":     # username will be added
                    username_ack = "ack"        # confirmation for the client
                    print(username_ack)
                    self.client_addresses.append(active_client_address)     # storing the address of the client
                    self.client_usernames.append(active_client_username)    # storing the name of the user
                    self.client_ack.append(username_ack)                    # storing the status of the client
                    self.oMessage.add_data("User <"+ active_client_username +"> logged in", active_client_address, self.SYSTEM)
                    print("list of users:", self.client_usernames)
                    print("list of addresses:", self.client_addresses)
                    print("list of stats:", self.client_ack)
                    conn.sendall(username_ack.encode((self.server_charset)))    # returns confirmation to client
                    Thread(args=(conn, active_client_address), target=self.handle_connection_out).start()
                    # starts handle_connection_out-thread
                # ------------------------- wait for input -------------------------
                elif username_ack == "ack":     # username is set
                    if self.client_ack[self.client_addresses.index(active_client_address)] == "closed": # this would
                        # mean that the equivalent handle_connection_out-Thread is closed => go to finalizer
                        break
                    if "closed" in self.client_ack: # should avoid real-time problems (threading + closing of conns)
                        sleep(1)
                    data = conn.recv(1024)  # awaits data
                    if (not data) | (len(data) == 0) | (data == ""):    # user wants to leave chat
                        print("=> EOF was sent, closing socket")
                        conn.sendall("".encode(self.server_charset))
                        break
                    data_decode = data.decode(self.server_charset)
                    if data_decode == "":
                        print("=> EOF was sent, closing socket")
                        break
                    print("received data from:", active_client_address, ": %s" % data_decode)
                    self.oMessage.add_data(data_decode, active_client_address, active_client_username)  # adds content
                    # of message to database
            except:
                print("Connection was closed on the Client Side")
                # print(sys.exc_info()[1])
                break

        # Finalizer

        if username_ack == "ack":   # test if username set
            if self.client_ack[self.client_addresses.index(active_client_address)] == "closed":     # if yes, the output
                # connection is already closed => name, address and ack of user can be removed safely
                self.oMessage.add_data("User <" + active_client_username + "> logged out", active_client_address, self.SYSTEM)
                conn.close()  # Close the connection
                del self.client_ack[self.client_addresses.index(active_client_address)]
                self.client_addresses.remove(active_client_address)
                self.client_usernames.remove(active_client_username)
            else:   # if not, output connection is still running => set client_ack to "closed"
                self.client_ack[self.client_addresses.index(active_client_address)] = "closed"
        else:   # if username not set, just close the connection
            conn.close()

    # ------------------------- handle_connection_out -------------------------
    # handles output and reads database to forward messages
    def handle_connection_out(self, conn, active_client_address):
        active_client_username = self.client_usernames[self.client_addresses.index(active_client_address)]
        n_message = self.oMessage.n_message
        # sets local n_message to the current value of global n_message
        # if n_message changes, new message is available to be forwarded

        # provides user with list of other acitve users
        data = "system message: list of other active users: "
        for i in self.client_usernames:
            if i != active_client_username:
                if data == "system message: list of other active users: ":
                    data = data + i
                else:
                    data = data + ", " + i
        conn.sendall(data.encode(self.server_charset))

        while True:
            try:
                if self.client_ack[self.client_addresses.index(active_client_address)] == "closed":     # if yes =>
                    # input connection is closed => go to finalizer
                    break
                if "closed" in self.client_ack:     # should avoid real-time problems (threading + closing of conns)
                    sleep(1)
                if self.oMessage.n_message > n_message: # if yes => new message is available in database
                    n_message = n_message + 1   # incr. local message counter
                    if self.oMessage.source_address[n_message] != active_client_address:    # if yes => message is from
                        # another user
                        print("sending data to:", active_client_address)
                        if self.oMessage.source_username[n_message] == self.SYSTEM:     # if yes => system message
                            data = "system message: " + self.oMessage.data[n_message]
                        else:   # forward message to client
                            data = self.oMessage.source_username[n_message] + " said: " + self.oMessage.data[n_message]
                        conn.sendall(data.encode(self.server_charset))
            except:
                print("Connection was closed on the Client Side")
                # print(sys.exc_info()[1])
                break

        # Finalizer

        if self.client_ack[self.client_addresses.index(active_client_address)] == "closed":
            # if already closed => input thread is closed => name, address and ack of the user can be removed safely
            self.oMessage.add_data("User <" + active_client_username + "> logged out", active_client_address, self.SYSTEM)
            conn.close()    # Close the connection
            del self.client_ack[self.client_addresses.index(active_client_address)]
            self.client_addresses.remove(active_client_address)
            self.client_usernames.remove(active_client_username)
        else:   # if not, input connection is still running => set client_ack to "closed"
            self.client_ack[self.client_addresses.index(active_client_address)] = "closed"

########################### main program ###########################
if __name__ == "__main__":
    oChat_Server = Chat_Server()    # creates server object
    oChat_Server.prepare_connection()   # prepares connection
    while True:
        oChat_Server.establish_connection()     # waits for clients
