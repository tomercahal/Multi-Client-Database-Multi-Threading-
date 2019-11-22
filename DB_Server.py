import socket
import pickle
import time
import threading
import os

ALL_SOCKETS_IN_USE = 'All sockets are being used at the time please wait'  # Used when all there are 10 users logged


class Server (object):  # This is server class
    def __init__(self):
        """The constructor of the Server"""
        self.IP = '127.0.0.1'  # The IP of the server.
        self.PORT = 220  # The chosen port to have the connection on
        self.someone_writing = False  # Used to know if someone can read at the time
        self.someone_reading = False  # Used to know if someone is reading at the time
        self.dict = {}  # The dict that will be updated each time, from unpickling
        self.database_file = 'database.txt'  # The file where the pickled dictionary is located
        self.users_allowed = 10  # This is the amount of users that are allowed to be logged in at the same time
        self.sem = threading.Semaphore(10)  # 10 is the number of threads that can be used

    def read_from_database(self, client_socket):
        if not self.someone_writing:  # If someone is not writing
            dictionary_file = open(self.database_file, 'r')  # Reading only, if there is someone writing, wait
            dictionary = pickle.loads(dictionary_file.read())  # Unpickling the dictionary so that we can send that to the user
            dictionary_file.close()
            return dictionary
        else:
            client_socket.send('Please wait, someone is currently writing to the database')
            self.read_from_database()

    def receive_from_client(self, client_sock):
        """This function receives the request from the client. It then classifies the user's request and does what he
        specified. The user has the option of writing (changing a value of a key),
         reading (requesting a key and getting it's value), adding (adding a key and a value to the database)
         seeing the entire database at the time, or typing help for seeing the options"""
        msg = client_sock.recv(1024)  # Recieve the data from the user
        if 'quit' in msg:
            client_sock.send('You have been successfully disconnected')
            self.sem.release()  # Clearing up the user's used thread for new available clients
            print 'User has been successfully disconnected ' + str(self.sem._Semaphore__value) + ' sockets left\r\n'
            return None
        elif 'view' in msg:
            client_sock.send(str(self.read_from_database(client_sock)))  # This will send the client the current dictionary)
        self.receive_from_client(client_sock)

#    def connect_to_server(self, client_sock):

    def handle_thread(self, client_sock):
        """ This function handles the clients. Since only users_allowed (10 at the time), can be connected and send
        requests at a time."""
        printed_once = False
        while self.sem._Semaphore__value == 0:
            if not printed_once:  # If we have not send a reply to the user yet
                print ALL_SOCKETS_IN_USE
                client_sock.send(ALL_SOCKETS_IN_USE)

        client_sock.send('Connecting you to the server now!')
        self.sem.acquire()  # Decreases the users logged in at the time (new thread opened)
        print 'New client connected to the database + ' + str(self.sem._Semaphore__value) + ' sockets left\r\n'
        self.receive_from_client(client_sock)

    def start(self):
        """Another main function in the server side, It is mainly used to aceept new clients through creating sockets
        and then directing the code to assaign them their jobs to find."""
        try:
            # check_sockets_active(OPEN_SOCKETS)  # change if got time to make sure every number is ran

            print('Server starting up on ip %s port %s' % (self.IP, self.PORT))
            # Create a TCP/IP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((self.IP, self.PORT))
            sock.listen(1)
            while True:
                print('Waiting for a new client')
                client_socket, client_address = sock.accept()  # Last step of being on a socket
                print('New client entered!')
                client_socket.sendall('Hello this is Tomer\'s server'.encode())
                thread = threading.Thread(target=self.handle_thread, args=(client_socket,))
                thread.start()

        except socket.error as e:
            print(e)


if __name__ == '__main__':
    s = Server()
    s.start()
