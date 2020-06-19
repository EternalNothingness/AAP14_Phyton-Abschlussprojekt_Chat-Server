# title: chat-client program
# author: EternalNothingness
# created: 13.06.2020
# last change: 16.06.2020

########################### imports ###########################
import socket
import sys
from threading import Thread

########################### classes ###########################
class Chat_Client(object):

    # ------------------------- init -------------------------
    def __init__(self, host='localhost', port=12345, client_charset='cp850'):
        self.host = host  # define host
        self.port = port  # define port
        self.client_address = self.host, self.port  # address consists of host and port
        self.client_charset = client_charset  # define character set
        self.username = ""
        self.socket_active = False

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object

    # ------------------------- Destructor -------------------------
    def __del__():
        close_socket()

    def close_socket(self):
        self.sendEOF()
        if self.s is not None:
            self.s.shutdown(SHUT_RDWR)
            self.s.close()

    def sendEOF(self):
        if self.s is not None:
            self.s.sendall("".encode(self.client_charset))

    # ------------------------- establish_connection -------------------------
    def establish_connection(self):
        self.s.connect(self.client_address)
        self.socket_active = True
        while True:
            self.username = input("username: ")
            if (len(self.username) > 0) & (len(self.username) <= 10):
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
            if self.socket_active != True:
                break
            try:
                # Muesste man auf Non-Blocking umschreiben
                data_recv = self.s.recv(1024)
                if data_recv is None: # Socket Close Signal
                    self.socket_active = False
                    break
                print((data_recv.decode(self.client_charset)))
            except:
                print("Connection was closed on the Server Side") #, sys.exc_info()[1])
                break

    # ------------------------- handle_connection_out -------------------------
    def handle_connection_out(self):
        while True:
            if self.socket_active != True:
                break
            try:
                # data_send = input("%s said: " % self.username)
                data_send = input()
                if data_send == "exit":
                    self.socket_active = False
                    self.sendEOF()
                    break
                if (len(data_send) <= 1024) & (len(data_send) > 0):
                    self.s.sendall(data_send.encode(self.client_charset))
                else:
                    print("Invalid message! Message length: <", len(data_send), ">")
            except:
                print("Connection was closed on the Server Side") #, sys.exc_info()[1])
                break

########################### main program ###########################
if __name__ == "__main__":
    oChat_Client = Chat_Client()
    oChat_Client.establish_connection()
    # oChat_Client.handle_connection()
