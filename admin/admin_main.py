# most of the methods defined here should contain try ... except blocks with the corresponding error
# in order to generate an adequate output

import socket
from settings_parser import SettingsParser
from communications.comms import CommunicationProtocol
import pickle
import hashlib

class AdminClass:
    def __init__(self, settings):
        self.settings = settings
        # we omit the credentials part right now
        self.source_sock = None
        self.server_sock = None
        self.source_settings = None
        self.source_communicator = None
        self.server_communicator = None
        self.client_list = None

    def main(self):
        while True:
            print("Choose an action:")
            print("1: Connect to source")
            print("2: Connect to server")
            print()
            print("3: Get sorting rule from source")
            print("4: Disconnect from source")
            print()
            print("5: Get client list from server")
            print("6: Set sorting rule")
            print("7: Restart server")
            print("8: Shutdown server")
            print("9: Disconnect from server")
            print("10: Connect server to source")
            print("11: Close admin panel")

            # to implement: get sort rule from source, set rule to server
            choice = input()

            if choice == "1":
                self.connect_to_source()
            elif choice == "2":
                self.connect_to_server()
            elif choice == "3":
                self.get_sort_rule()
            elif choice == "4":
                self.disconnect_source()
            elif choice == "5":
                self.get_client_list()
                index = 1
                for clie in self.client_list:
                    print(index, ":", clie)
                    index += 1
            elif choice == "6":
                self.set_sort_rule()
            elif choice == "7":
                self.restart_server()
            elif choice == "8":
                self.shutdown_server()
            elif choice == "9":
                self.disconnect_server()
            elif choice == "10":
                self.connect_server_to_source()
            elif choice == "11":
                break
            else:
                print("Unknown command")

    def connect_to_source(self):
        self.source_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.source_sock.connect((self.settings.getValue("source_address"), int(self.settings.getValue("source_port"))))
        self.source_communicator = CommunicationProtocol(self.source_sock)

        credentials_tuple = b"".join([self.settings.getValue("username").encode(), b":", self.settings.getValue("password").encode()])
        tuple_hashed = hashlib.md5(credentials_tuple).hexdigest()
        self.source_communicator.sendMessage(pickle.dumps(tuple_hashed), b"ADMIN_CREDENTIALS")
        cred_status = self.source_communicator.receiveMessage(b"ADMIN_CREDENTIALS_STATUS")
        if cred_status == b"STATUS_OK":
            print("Successfully connected to source")
        else:
            print("Incorrect credentials")
            self.source_communicator = None
            self.source_sock.close()

    def connect_to_server(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.connect((self.settings.getValue("server_address"), int(self.settings.getValue("server_port"))))
        self.server_communicator = CommunicationProtocol(self.server_sock)

        credentials_tuple = b"".join([self.settings.getValue("username").encode(), b":", self.settings.getValue("password").encode()])
        tuple_hashed = hashlib.md5(credentials_tuple).hexdigest()
        self.server_communicator.sendMessage(pickle.dumps(tuple_hashed), b"ADMIN_CREDENTIALS")
        cred_status = self.server_communicator.receiveMessage(b"ADMIN_CREDENTIALS_STATUS")
        if cred_status == b"STATUS_OK":
            print("Successfully connected to server")
        else:
            print("Incorrect credentials")
            self.server_communicator = None
            self.server_sock.close()

    def get_sort_rule(self):
        self.source_communicator.sendMessage(b"GET_SETTINGS", b"ADMIN_COMMAND")
        recv_data = self.source_communicator.receiveMessage(b"COMMAND_PASSED")
        self.source_settings = pickle.loads(recv_data)

    def disconnect_source(self):
        self.source_communicator.sendMessage(b"ADMIN_DISCONNECTED", b"ADMIN_COMMAND")
        self.source_sock.close()

    def get_client_list(self):
        self.server_communicator.sendMessage(b"GET_CLIENT_LIST", b"ADMIN_COMMAND")
        recv_data = self.server_communicator.receiveMessage(b"COMMAND_PASSED")
        self.client_list = pickle.loads(recv_data)

    def restart_server(self):
        self.server_communicator.sendMessage(b"RESTART_SERVER", b"ADMIN_COMMAND")
        self.server_sock.close()

    def shutdown_server(self):
        self.server_communicator.sendMessage(b"CLOSE_SERVER", b"ADMIN_COMMAND")
        self.server_sock.close()

    def disconnect_server(self):
        self.source_communicator.sendMessage(b"ADMIN_DISCONNECTED", b"ADMIN_COMMAND")
        self.server_sock.close()

    def set_sort_rule(self):
        self.server_communicator.sendMessage(b"SET_SORT_RULE", b"ADMIN_COMMAND")
        self.server_communicator.receiveMessage(b"SORT_RULE_REQUEST")
        send_chunk = pickle.dumps(self.source_settings)
        self.server_communicator.sendMessage(send_chunk, b"ADMIN_SORT_RULE")

    def connect_server_to_source(self):
        self.server_communicator.sendMessage(b"CONNECT_TO_SOURCE", b"ADMIN_COMMAND")

if __name__ == "__main__":
    sets = SettingsParser()
    sets.loadSettings("settings.cfg")
    admin = AdminClass(sets)
    admin.main()
