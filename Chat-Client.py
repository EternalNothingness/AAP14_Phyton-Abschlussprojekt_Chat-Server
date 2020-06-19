# title: chat-client program
# author: EternalNothingness
# created: 13.06.2020
# last change: 16.06.2020

########################### imports ###########################
import socket
import sys
from threading import Thread

########################### classes ###########################
class Chat_CLient(object):

    # ------------------------- init -------------------------
    def __init__(self, host='localhost', port=12345, client_charset='cp850'):
        self.host = host  # define host
        self.port = port  # define port
        self.client_address = self.host, self.port  # address consists of host and port
        self.client_charset = client_charset  # define character set
        self.username = ""

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object

    # ------------------------- establish_connection -------------------------
    def establish_connection(self):
        self.s.connect(self.client_address)
        while True:
            self.username = input("username: ")
            if self.username != "":
                if len(self.username) <= 10:    # max. name length: 10
                    self.s.sendall(self.username.encode(self.client_charset))
                    data_recv = self.s.recv(1024)
                    data_recv_decode = data_recv.decode(self.client_charset)
                    if data_recv_decode == "ack":
                        print("username accepted")
                        break
            print("username declined")
        Thread(args=(), target=self.handle_connection_in).start()
        Thread(args=(), target=self.handle_connection_out).start()

    # ------------------------- handle_connection_in -------------------------
    def handle_connection_in(self):
        while True:
            try:
                data_recv = self.s.recv(1024)
                print((data_recv.decode(self.client_charset)))
            except:
                print("Unexpected error:", sys.exc_info()[1])
                break
        self.s.close()

    # ------------------------- handle_connection_out -------------------------
    def handle_connection_out(self):
        while True:
            try:
                # data_send = input("%s said: " % self.username)
                data_send = input()
                if data_send == "":
                    break
                if len(data_send) <= 1024:
                    self.s.sendall(data_send.encode(self.client_charset))
                else:
                    print("Too long message!")
            except:
                print("Unexpected error:", sys.exc_info()[1])
                break
        self.s.close()

########################### main program ###########################
oChat_Client = Chat_CLient()
oChat_Client.establish_connection()
# oChat_Client.handle_connection()
