import socket
from communications.comms import CommunicationProtocol
from communications_large.comms_large import LargeCommunicationProtocol
import random
import pickle
from settings_parser import SettingsParser
import importlib
from listen_admin import ListenerAdmin

# it will become a class reference (dynamically imported)
ElementUnit = None

class ExternalSource:
    def __init__(self, settings):
        self.settings = settings
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((socket.gethostname(), int(self.settings.getValue("server_listen_port"))))
        self.sock.listen(5)
        print("Server Socket address:", self.sock.getsockname())

        self.admin_listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.admin_listen_socket.bind((socket.gethostname(), int(self.settings.getValue("admin_listen_port"))))
        self.admin_listen_socket.listen(5)
        print("Admin Socket address:", self.admin_listen_socket.getsockname())

        global ElementUnit
        import_fixed = self.settings.getValue("sort_rule").replace("/", ".")
        ElementUnit = importlib.import_module(import_fixed).ElementUnit

    def run(self):
        admin_listener = ListenerAdmin(self.admin_listen_socket, self.settings)
        admin_listener.start()

        server_socket, address = self.sock.accept()
        print("Server connected to data source with address", address)

        large_communicator = LargeCommunicationProtocol(server_socket)
        communicator = large_communicator.get_communicator()
        chunk_number = 0
        while True:
            print("Generating a new batch of random numbers")

            # The application should have a ~2-4 MB read/write buffer, since accessing the disk for every 4 KB of data is very slow
            numbers = bytearray()
            with open("numbers_test", "wb") as fileout:
                for i in range(500):
                    print(i)
                    numbers.extend(ElementUnit.get_random_sequence(4096))
                    if len(numbers) > 2100000: # approx 2 MB
                        fileout.write(numbers)
                        numbers = bytearray()
                fileout.write(numbers) # in case there is anything left

            print("Sending the batch to the server")
            large_communicator.sendMessage("numbers_test", b"CHUNK_INITIAL")

            print("Waiting for response")
            # should be changed, since messages could be very large
            # (hundreds of GBs) and lead to memory errors
            chunk_number += 1
            large_communicator.receiveMessage("%d" % chunk_number, b"CHUNK_MERGED")

            print("Sorted chunk received from server")

        server_socket.close()
        self.sock.close()

if __name__ == "__main__":
    sets = SettingsParser()
    sets.loadSettings("settings.cfg")
    source = ExternalSource(sets)
    source.run()
