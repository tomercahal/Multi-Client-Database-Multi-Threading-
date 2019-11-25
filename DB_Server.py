import socket
import pickle
import re
import threading

ALL_SOCKETS_IN_USE = 'All sockets are being used at the time please wait'  # Used when all there are 10 users logged


class Server (object):  # This is server class
    def __init__(self):
        """The constructor of the Server"""
        self.IP = '127.0.0.1'  # The IP of the server.
        self.PORT = 220  # The chosen port to have the connection on
        self.thread_writing = -1  # Used to know if someone can read at the time + thread using
        self.thread_reading = -1  # Used to know if someone is reading at the time + thread using
        self.dict = {}  # The dict that will be updated each time, from unpickling
        self.database_file = 'database.txt'  # The file where the pickled dictionary is located
        self.active_users = []  # This is a list containing hte threads that are active and if there are any open
        self.users_allowed = 10  # This is the amount of users that are allowed to be logged in at the same time
        self.sem = threading.Semaphore(self.users_allowed)  # users allowed is a variable making the program dynamic

    def read_from_database(self, client_socket, thread_num):
        print '\r\nInside read database: Current thread reading: ' + str(self.thread_reading)  # for debugging
        print 'Inside read database: Current thread writing: ' + str(self.thread_writing)  # for debugging
        if thread_num == self.thread_writing or self.thread_writing == -1:  # checking if open for read or reader is writer
            dictionary_file = open(self.database_file, 'r')  # Reading only, if there is someone writing, wait
            dictionary = pickle.loads(dictionary_file.read())  # Unpickling the dictionary so that we can send that to the user
            dictionary_file.close()
            return dictionary
        else:
            client_socket.send('Please wait, someone is currently writing to the database')
            print 'sending to user please wait'
            while self.thread_writing != -1:  # This basically waits until there is not a thread writing or adding
                continue
            return self.read_from_database(client_socket, thread_num)

    def update_database(self, db_dict, client_sock, thread_num):
        """This function updates the database by receiving a dictionary as input and pickling it into the database"""
        print '\r\nInside update database: Current thread reading: ' + str(self.thread_reading)  # for debugging
        print 'Inside update database: Current thread writing: ' + str(self.thread_writing)  # for debugging
        if thread_num == self.thread_reading or self.thread_reading == -1:   # checking if open for read or reader is writer
            dictionary_file = open(self.database_file, 'w')  # Writing only, if there is someone writing, wait
            dictionary_file.write(pickle.dumps(db_dict))
            dictionary_file.close()
        else:
            client_sock.send('Please wait someone is currently reading from the database')
            while self.thread_reading != -1:  # This basically waits until there isn't a thread reading
                continue
            return self.update_database(db_dict, client_sock, thread_num)
        self.thread_writing = -1  # Changing now because there isn't someone writing anymore

    def break_further_input(self, type_of_request, client_sock, thread_num):
        """This function is called to get the further input for the specific modes that need them,
        such as write read and add. It checks if what the user has entered is valid and does as requested or
        returns an error message."""
        request_fulfilled = False
        while not request_fulfilled:
            further_input = client_sock.recv(1024)  # Getting the further input for the request
            self.thread_reading = thread_num  # So that writers can not access
            dictionary = self.read_from_database(client_sock, thread_num)  # Getting the dictionary can wait if someone is writing
            if type_of_request == 'read':
                if further_input in dictionary.keys():  # Checking if the user requested key is in the dictionary
                    client_sock.send('The value of the key: ' + further_input + ', is: ' +
                                     dictionary[further_input] + '\r\n')  # Returning the value of the requested key
                    request_fulfilled = True   # This is to tell the server it can get a new request now
                    self.thread_reading = -1  # No longer reading can free it up
                else:
                    client_sock.send('ERROR, key not found please try again.\r\n')
            elif type_of_request is 'add' or 'write':
                if re.search('.*:.*', further_input):  # Checking if the user has entered the correct format key:value
                    dict_key, dict_value = further_input.split(':')  # Now a list containing the key and the value
                    if type_of_request == 'write':
                        if dict_key in dictionary.keys():
                            dictionary[dict_key] = dict_value  # Changing the key's value
                            client_sock.send('The value of the key: ' + dict_key + ' has been changed to: ' + dict_value
                                             + ' successfully!\r\n')
                            self.update_database(dictionary, client_sock, thread_num)  # updating the database
                            request_fulfilled = True  # This is to tell the server it can get a new request now
                            self.thread_reading = -1  # No longer reading can free it up
                        else:
                            client_sock.send('ERROR, key not found please try again.\r\n')
                            continue
                    elif type_of_request == 'add':
                        dictionary[dict_key] = dict_value  # Just added another value to the dictionary
                        client_sock.send('The key: '+ dict_key + ', and the value: ' + dict_value +
                                         ' have been added to the database\r\n')
                        self.update_database(dictionary, client_sock, thread_num)  # updating the database
                        request_fulfilled = True
                        self.thread_reading = -1  # No longer reading can free it up
                else:
                    client_sock.send('ERROR, please use this format for write and add mode key:value\r\n')

    def receive_from_client(self, client_sock, thread_num):
        """This function receives the request from the client. It then classifies the user's request and does what he
        specified. The user has the option of writing (changing a value of a key),
         reading (requesting a key and getting it's value), adding (adding a key and a value to the database)
         seeing the entire database at the time, or typing help for seeing the options"""
        message = client_sock.recv(1024)  # Receive the data from the user
        while 'quit' != message:
            print 'Thread number: ' + str(thread_num) + ', asked to: ' + message + '\r\n'
            if 'view' == message:
                client_sock.send(str(self.read_from_database(client_sock, thread_num)))  # This will send the client the current dictionary)
            elif 'write' == message or 'add' == message:
                self.thread_writing = thread_num
                self.break_further_input(message, client_sock, thread_num)  # same for add write or read
            elif 'read' == message:
                self.thread_reading = thread_num
                self.break_further_input(message, client_sock, thread_num)  # same for add write or read
            message = client_sock.recv(1024)  # Getting the new input
        if 'quit' == message:
            client_sock.send('You have been successfully disconnected')
            self.sem.release()  # Clearing up the user's used thread for new available clients
            self.active_users[thread_num-1] = 0  # -1 because indexes start at 0
            print 'User has been successfully disconnected ' + str(self.sem._Semaphore__value) + ' sockets left\r\n'
            return None

    def connect_client(self, client_sock):
        """This function knows how to handle many clients coming in, it let's a user know if all the sockets are full
        and he has to wait. It returns the thread number that it will be assigned later."""
        connection_available = True
        printed_once = False
        while connection_available:  # used so
            for user in range(self.users_allowed):
                if self.active_users[user] == 0:
                    self.active_users[user] = self.active_users.index(0) + 1
                    return self.active_users[user]  # We have found a number that can be assigned to the thread
            if not printed_once:  # If we have not send a reply to the user yet
                print ALL_SOCKETS_IN_USE
                client_sock.send(ALL_SOCKETS_IN_USE)
                printed_once = True  # Now the user won't get the message anymore

    def handle_thread(self, client_sock, thread_num):
        """ This function handles the clients. Since only users_allowed (10 at the time), can be connected and send
        requests at a time."""
        print 'you are thread number: ' + str(thread_num)
        client_sock.send('Connecting you to the server now!')
        self.sem.acquire()  # Decreases the users logged in at the time (new thread opened)
        print 'New client connected to the database + ' + str(self.sem._Semaphore__value) + ' sockets left\r\n'
        self.receive_from_client(client_sock, thread_num)

    def zeroing_active_users_list(self):
        """This function adds the amount of sockets that are allowed (The value of user_allowed)
        It is set as zero (it means that there isn't someone using that socket, else if there is a number then
        it is in use"""
        for user in range(self.users_allowed):
            self.active_users.append(0)  # making all of the active users slot value, zero

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
                print('\r\nWaiting for a new client')
                client_socket, client_address = sock.accept()  # Last step of being on a socket
                print('New client entered!')
                client_socket.sendall('Hello this is Tomer\'s server'.encode())  # First connection message
                thread_number = self.connect_client(client_socket)  # This function
                thread = threading.Thread(target=self.handle_thread, args=(client_socket, thread_number))
                thread.start()

        except socket.error as e:
            print(e)


if __name__ == '__main__':
    s = Server()
    s.zeroing_active_users_list()  # Adding the amount of sockets that can be used with the database
    s.start()
