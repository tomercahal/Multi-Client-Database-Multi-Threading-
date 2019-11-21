import socket
import time
import multiprocessing
import hashlib
import time
import threading
import os

FIRST_AND_HELP_MESSAGE = 'Hi, and welcome to Tomer\' database\r\n You can choose between many different requests ' \
                         'to databse. Would you like to:\r\n' \
                         'Write to the database (enter a key in the database and can change the value of it) - press w' \
                         '\r\nRead from the database (enter a key and get the value of it) - press r\r\n' \
                         'Add a key and a value to the databse - press a\r\n' \
                         'View the whole database - press v\r\n' \
                         'Quit Tomer\'s database - press q' \
                         'For help - press h.\r\n'


def write_to_database(c, char_request):
    """This function is called when the user is in write mode and he wants to write to a specific key"""
    print 'User is in write mode'


def read_from_database(c, char_request):
    """This function is called when the user is in read mode and he wants to write to a specific key"""
    print 'User is in read mode'


def add_to_database(c, char_request):
    """This function is called when the user is in add mode and wants to add a key and a value to the database"""
    print 'User is in add mode'


def quit_view_help(c, char_request):
    """This function is called when the user requested either quit view or help, which means he does not need any extra
    input to send to the server"""
    print 'User is in quit, view or help mode'
    if char_request == 'h':
        print FIRST_AND_HELP_MESSAGE  # The first message that is used which is also used as help.
    elif char_request == 'q':
        c.send_to_server(c, 'quit')
        print c.get_server_output()
        os._exit()  # closing the client's program so that he won't get an error
    elif char_request == 'v':
        c.send_to_server(c, 'view')
        print c.get_server_output()  # This prints to the client if someone is not writing or adding to it!!!!!!!!!!!!!!!
    return True


USER_OPTIONS = {'w': write_to_database, 'r': read_from_database, 'a': add_to_database, 'q': quit_view_help
                , 'v': quit_view_help, 'h': quit_view_help}


class Client(object):  # This is the Client class

    def __init__(self):
        """The constructor of the Client"""
        self.IP = '127.0.0.1'  # The Ip of the client.
        self.PORT = 220  # The port of the client.
        self.type = None  # At the start, the client has no type of request later it is 'add' or 'read'
        self.server_socket = None  # still need to connect

    def start(self):
        """Sort of like the main function, it binds a socket connection to the server and gets the jobs that he asks."""
        try:
            print('Trying to connect to IP %s PORT %s' % (self.IP, self.PORT))
            # Create a TCP/IP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.IP, self.PORT))
            self.server_socket = sock  # Now the Client's server value has the socket's reference
            server_connect_response = self.server_socket.recv(1024)  # Getting the server's response to the 1st connection.
            while 'connecting' not in server_connect_response:  # When we are connected the server sends
                # message with the word connecting in it
                print server_connect_response
                server_connect_response = self.server_socket.recv(1024)  # Waiting for the new response
            print server_connect_response  # This just let's the user know he is connected now
            self.get_user_request()
        except socket.error as e:
            print(e)
            self.server_socket.close()

    def get_user_request(self):
        """This function..."""
        print FIRST_AND_HELP_MESSAGE
        keep_asking = True
        while keep_asking:
            mode_char = raw_input('Please enter the mode that you want: ')  # Here the user enters the mode he wants
            if mode_char in USER_OPTIONS.keys():
                keep_asking = USER_OPTIONS[mode_char](self, mode_char)
                # Calling the appropriate function based on the user's input. This is sick!!!
            else:
                print 'ERROR, you did not enter one of the supported modes. Modes avaiable: w, r, a, v, q, h'

    def get_server_output(self):
        return self.server_socket.recv(1024)

    def send_to_server(self, data_to_send):
        """This function..."""
        self.server_socket.send(data_to_send)  #sending the final user request to the server


if __name__ == '__main__':
    run = 0  # since on the other runs we don't need to accept a new socket anymore, we stay connected.
    client = Client()  # Creating a client
    client.start(run)  # Using the client's start function
