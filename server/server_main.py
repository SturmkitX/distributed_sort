# Main module for server

import socket
import threading
import listen_thread
from listener_thread_admin import ListenThreadAdmin
from communications.comms import CommunicationProtocol
from communications_large.comms_large import LargeCommunicationProtocol
from merge_files import MergeClass
from settings_parser import SettingsParser
import os
import signal

import close_sentinel

class ServerClass:
    def __init__(self, settings):
        self.server_socket = None
        self.source_socket = None
        self.admin_listen_socket = None
        self.settings = settings

    def main(self):
        self.admin_listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.admin_listen_socket.bind((socket.gethostname(), int(self.settings.getValue("admin_listen_port"))))
        self.admin_listen_socket.listen(5)
        print("Admin Socket address:", self.admin_listen_socket.getsockname())

        admin_listener = ListenThreadAdmin(self.admin_listen_socket, self.settings)
        admin_listener.start()

        # connect to the external source
        self.source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while self.settings.getValue("connect_to_source") is None:
            pass
        self.source_socket.connect((self.settings.getValue("source_address"), int(self.settings.getValue("source_port"))))
        large_communicator = LargeCommunicationProtocol(self.source_socket)
        communicator = large_communicator.get_communicator()

        # Create an INET, STREAMing socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # bind the socket to a public host a a well-known port
        self.server_socket.bind((socket.gethostname(), int(self.settings.getValue("server_port"))))

        # become a server socket
        self.server_socket.listen(5)

        while True:
            # receiving initial batch of numbers
            large_communicator.receiveMessage("numbers_test", b"CHUNK_INITIAL")
            print("Initial chunk received from external source")

            # create the listening thread
            listening_thread = listen_thread.ListenThread(self.server_socket, self.source_socket, self.settings)

            print("The server\'s ip address is:", self.server_socket.getsockname())
            print("\n")

            listening_thread.start()

            # wait for the listening thread to finish
            listening_thread.join()

            # external close message has been received
            if close_sentinel.CloseSentinel.close_flag == True:
                break

            # merge the files
            merger = MergeClass(self.settings)
            merged_bytes_location = merger.merge_final()

            print("Sending merged chunks back to external source")
            large_communicator.sendMessage(merged_bytes_location, b"CHUNK_MERGED")
            print("Finished sending merged chunks to external source")
            os.unlink(merged_bytes_location)



        # close connection (it will be already closed if entered here)
        self.server_socket.close()
        self.source_socket.close()
        self.admin_listen_socket.close()
        os.kill(os.getpid(), signal.SIGKILL)

if __name__ == "__main__":
    while True:
        settings = SettingsParser()
        settings.loadSettings("settings.cfg")
        server = ServerClass(settings)
        server.main()
