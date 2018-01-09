# Main connetion handler thread

import socket
import threading
import listen_thread
import os
import signal
from communications.comms import CommunicationProtocol
import generate_chunks
import pickle

from close_sentinel import CloseSentinel

class HandlerThreadAdmin(threading.Thread):
    def __init__(self, admin_socket, address, settings):
        threading.Thread.__init__(self)
        self.admin_socket = admin_socket
        self.address = address
        self.settings = settings

    def run(self):
        # constantly get info from the socket
        communicator = CommunicationProtocol(self.admin_socket)

        # get the admin credentials
        recv_cred = pickle.loads(communicator.receiveMessage(b"ADMIN_CREDENTIALS"))
        if recv_cred in self.settings.getValue("accepted_admins"):
            communicator.sendMessage(b"STATUS_OK", b"ADMIN_CREDENTIALS_STATUS")
        else:
            communicator.sendMessage(b"STATUS_INCORRECT", b"ADMIN_CREDENTIALS_STATUS")
            self.admin_socket.close()
            return

        print("An administrator connected with IP address", self.address)

        while True:
            command = communicator.receiveMessage(b"ADMIN_COMMAND")
            print(command)
            if command == b"CLOSE_SERVER":
                sentinel = CloseSentinel(self.settings)
                sentinel.sendShutdownSignal()
                break
            elif command == b"SET_SORT_RULE":
                communicator.sendMessage(b"", b"SORT_RULE_REQUEST")
                recv_chunk = pickle.loads(communicator.receiveMessage(b"ADMIN_SORT_RULE"))
                with open(recv_chunk["sort_rule"] + ".py", "wb") as fileout:
                    fileout.write(recv_chunk["rule_data"])
                    # fileout.flush()
                # self.settings.addValue("sort_rule", recv_chunk["sort_rule"].replace("/", "."))
                self.settings.addValue("sort_rule", recv_chunk["sort_rule"])
            elif command == b"CONNECT_TO_SOURCE":
                self.settings.addValue("connect_to_source", True)
            elif command == b"RESTART_SERVER":
                sentinel = CloseSentinel(self.settings)
                sentinel.sendRestartSignal()
                break
            elif command == b"GET_CLIENT_LIST":
                client_list = []
                for cli in generate_chunks.ChunkClass.connected_clients:
                    client_list.append(cli.getpeername())
                communicator.sendMessage(pickle.dumps(client_list), b"COMMAND_PASSED")
            elif command == b"ADMIN_DISCONNECTED":
                break

        # close connection (it has already been closed)
        self.admin_socket.close()
