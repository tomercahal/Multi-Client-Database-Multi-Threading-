import socket
import time
import threading
import os

ALL_SOCKETS_IN_USE = 'All sockets are being used at the time please wait'  # Used when all there are 10 users logged


class Server (object):  # This is server class
    def __init__(self):
        """The constructor of the Server"""
        self.IP = '127.0.0.1'  # The IP of the server.
        self.PORT = 220  # The chosen port to have the connection on
        self.HASH = 'EC9C0F7EDCC18A98B1F31853B1813301'  # This is the hash that we need to match
        self.START_NUM = 3735118500  # The number that the hash starts with(very close to actual one
        self.FINISH_NUM = 9999999999  # The number that the hash ends with
        self.CHOSEN_RANGE = 10000  # This is the range that the client will go over each time
        self.someone_writing = False  # Used to know if someone can read at the time
        self.HASH_FOUND = 'The hash has been found! it is: '  # Just a simple message it will be used later
        self.dict = {}  # The dict that will be updated each time, from unpickling
        self.database_file = 'database.txt'  # The file where the pickled dictionary is located
        self.users_allowed = 10  # This is the amount of users that are allowed to be logged in at the same time
        self.sem = threading.Semaphore(10)  # 10 is the number of threads that can be used

    def read_from_database(self):
        pass

    def receive_from_client(self, client_sock):
        """This function receives the request from the client. It then classifies the user's request and does what he
        specified. The user has the option of writing (changing a value of a key),
         reading (requesting a key and getting it's value), adding (adding a key and a value to the database)
         seeing the entire database at the time, or typing help for seeing the options"""
        msg = client_sock.recv(1024)  # Recieve the data from the user
        if 'quit' in msg:
            self.sem.release()


    def handle_thread(self, client_sock):
        """ This function handles the clients. Since only users_allowed (10 at the time), can be connected and send
        requests at a time."""
        while self.sem._Semaphore__value == 0:
            print ALL_SOCKETS_IN_USE
            client_sock.send(ALL_SOCKETS_IN_USE)
            time.sleep(3)  # Waiting so that the user won't get so many can not connect messages

        client_sock('Connecting you to the server now!')
        print 'New client connected directly to the database + ' + self.sem._Semaphore__value + 'left'
        self.sem.acquire()  # Decreases the users logged in at the time (new thread opened)
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
                client_socket.send('Hi please enter what action you want to do.')
                thread = threading.Thread(target=self.handle_thread, args=client_socket)
                thread.start()
                msg = client_socket.recv(1024)
                print('Received message: %s' % msg.decode())
                for s in self.OPEN_SOCKETS:
                    thread_each_socket = threading.Thread(target=self.handle_client, args=(s,))  # Creating a thread
                    thread_each_socket.start()

        except socket.error as e:
            print(e)

if __name__ == '__main__':
    s = Server()
    s.start()
    # def handle_client(self, client_socket):
    #     """This function is the main function that calls all the other ones. It is sort of like the manager. From here
    #     we will send a new range to the clients and get their calculations to see it they have the match. If they don't
    #     we will send them a new set of numbers, till we don't have anymore left."""
    #     while self.START_NUM < self.FINISH_NUM:
    #         thread = threading.Thread(target=self.send_to_client, args=(client_socket,))  # Creating the thread
    #         thread.start()  # activating the thread and now it goes to send_to_client func
    #         thread_recv = threading.Thread(target=self.receive_from_client, args=(client_socket,))  # The receiving thread, gets input from client
    #         thread_recv.start()
    #         thread_recv.join()  # waiting for the receiving thread, cause we must get an answer if it was in the range.
    #         self.START_NUM += self.CHOSEN_RANGE  # increasing the global variable until we get to finish num.
    #
    # def send_to_client(self, client_socket):
    #     """In this function I will send the client the job he has do to(basically his part) in
    #      finding the 10 digit number.
    #      The format of the data will be: [hash code wanted]/start of job/end of job"""
    #     data_to_send = "%s/%s/%s" % (self.HASH.lower(), self.START_NUM, self.START_NUM + self.CHOSEN_RANGE)
    #     print 'Sending to the client: ' + data_to_send  # The data that is sent to the client
    #     client_socket.sendall(data_to_send)
    #
    # def receive_from_client(self, client_socket):
    #     """In this function I will receive the status of the completed job from the client. He will send me
    #     back the status of the job using this format: [Bool]/None or the number if found"""
    #     response = client_socket.recv(1024)
    #     parts = response.split('/')
    #     print parts
    #     bool_found = parts[0]
    #     print parts[0], 'num is: ' + parts[1]
    #     if not bool_found:  # if the number is found WEIRDD
    #         print self.HASH_FOUND + parts[1]
    #         os._exit(0)  # Terminates the current program since the number has been found
    #     else:
    #         return