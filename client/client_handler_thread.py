import socket
import threading
import pickle
from communications.comms import CommunicationProtocol
from rule_handler import RuleHandler

class ClientHandlerThread(threading.Thread):
    def __init__(self, settings, thread_number):
        threading.Thread.__init__(self)
        self.settings = settings
        self.thread_number = thread_number

    def run(self):
        # create an INET, STREAMing socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect to the server
        self.client_socket.connect((self.settings.getValue("server_address"), int(self.settings.getValue("server_port"))))
        communicator = CommunicationProtocol(self.client_socket)

        # send a notification to the server to know
        # this server is a client
        communicator.sendMessage(b"CLIENT", b"CLIENT_TYPE")

        # receive the sort_rule
        rule_dict = pickle.loads(communicator.receiveMessage(b"SORT_RULE"))
        RuleHandler.generate_rule_file(rule_dict)
        communicator.sendMessage(b"", b"SORT_RULE_RECEIVED")

        # main loop
        while True:
            recv_chunk = communicator.receiveMessage(b"CHUNK_COMPLETE")

            if recv_chunk is not None:
                print("Thread %d: Correct chunk MD5" % self.thread_number)
            else:
                print("Thread %d: Chunk MD5 is incorrect!" % self.thread_number)
                communicator.sendMessage(b"CHUNK_ERROR", b"CHUNK_SORTED")
                continue
            # check for end of chunks
            if recv_chunk[-10:] == b"NONE_LEFT_":
                break

            # construct the list of integers, based on the received chunks
            int_list = pickle.loads(recv_chunk)

            # then, sort the list
            int_list.sort()

            # transform it back to a list of bytes, ending with CHUNK_SORTED
            # send it to the server
            communicator.sendMessage(pickle.dumps(int_list), b"CHUNK_SORTED")

        # close connection
        self.client_socket.close()
