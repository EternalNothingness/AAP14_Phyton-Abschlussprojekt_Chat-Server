# title: chat-client program
# author: EternalNothingness
# created: 13.06.2020
# last change: 13.06.2020

########################### imports ###########################
import socket

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
                        break

    # ------------------------- handle_connection -------------------------
    def handle_connection(self):
        while True:
            data_send = input("Bitte Botschaft eingeben: ")
            if data_send == "":
                break
            self.s.sendall(data_send.encode(self.client_charset))
            data_recv = self.s.recv(1024)
            print("got from server: %s" % data_recv.decode(self.client_charset))
        self.s.close()

########################### main program ###########################
oChat_Client = Chat_CLient()
oChat_Client.establish_connection()
oChat_Client.handle_connection()
