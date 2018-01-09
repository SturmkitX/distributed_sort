# The connections listening thread

import socket
import threading
import handler_thread
import handler_thread_admin
import sys
import generate_chunks
from communications.comms import CommunicationProtocol
import request_sentinel
from merge_files import MergeClass
import close_sentinel

class ListenThread(threading.Thread):
    def __init__(self, server_socket, source_socket, settings):
        threading.Thread.__init__(self)
        self.server_socket = server_socket
        self.source_socket = source_socket
        self.settings = settings

    def run(self):
        conn_counter = 0
        communicator = CommunicationProtocol(self.source_socket)

        # suppose the initial chunk of data has been received
        generate_chunks.ChunkClass.chunks = open("numbers_test", "rb")
        generate_chunks.ChunkClass.chunk_number = 0
        generate_chunks.ChunkClass.chunks_received = 0
        generate_chunks.ChunkClass.generate_over = False
        while True:
            print("Waiting for client connection")
            (client_socket, address) = self.server_socket.accept()

            # get the type of client (simple client or administrator)
            client_type = CommunicationProtocol(client_socket).receiveMessage(b"CLIENT_TYPE").decode()

            conn_counter += 1
            if client_type == "SENTINEL_CLOSE_SERVER":
                break
            if client_type == "SENTINEL_SHUTDOWN_SERVER":
                with open("server_exit_status.dat", "w") as fileout:
                    fileout.write("DO_NOT_REPEAT\n")
                close_sentinel.CloseSentinel.close_flag = True
                break
            if client_type == "SENTINEL_RESTART_SERVER":
                # close_sentinel.CloseSentinel.sentinel_id = 0
                with open("server_exit_status.dat", "w") as fileout:
                    fileout.write("DO_REPEAT\n")
                close_sentinel.CloseSentinel.close_flag = True
                break
            else:
                newConn = handler_thread.HandlerThread(client_socket, address, conn_counter, self.settings)
            generate_chunks.ChunkClass.connected_clients.append(client_socket)

            newConn.start()
