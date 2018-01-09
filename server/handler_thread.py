# Main connetion handler thread

import socket
import threading
import generate_chunks
from close_sentinel import CloseSentinel
from communications.comms import CommunicationProtocol
import pickle
import os

class HandlerThread(threading.Thread):
    def __init__(self, client_socket, address, client_id, settings):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.address = address
        self.client_id = client_id
        self.settings = settings
        print("A client connected with IP address:", self.address)
        print("Client ID:", self.client_id)

    def run(self):
        # send chunks to the client
        communicator = CommunicationProtocol(self.client_socket)

        # send sort_rule to the client
        rule_dict = dict()
        rule_dict["sort_rule"] = self.settings.getValue("sort_rule")
        with open(rule_dict["sort_rule"] + ".py", "rb") as filein:
            rule_dict["rule_data"] = filein.read()
        communicator.sendMessage(pickle.dumps(rule_dict), b"SORT_RULE")
        communicator.receiveMessage(b"SORT_RULE_RECEIVED")


        chunk_id = 0 # there is no chunk with ID 0
        while True:
            # check if the previous chunk_id is still present
            if not os.path.exists("chunks_pending/%d" % chunk_id):
                chunk_id, chunk = generate_chunks.get_chunk()

            # if chunk_id is -1, then all chunks have been passed
            # we must signal the client that we are done
            if chunk_id == -1:
                communicator.sendMessage(b"", b"NONE_LEFT_CHUNK_COMPLETE")
                print("End of file reached")
                break
            communicator.sendMessage(pickle.dumps(chunk), b"CHUNK_COMPLETE")

            with open("chunks_pending/%d" % chunk_id, "wb") as fileout:
                pickle.dump(chunk, fileout)

            # wait for the client to send the sorted chunk
            recv_chunk = communicator.receiveMessage(b"CHUNK_SORTED")
            if recv_chunk == b"CHUNK_ERROR":
                continue

            generate_chunks.increment_received()
            os.unlink("chunks_pending/%d" % chunk_id)

            # write the received chunk to its corresponding file
            with open("chunks/%d" % chunk_id, "wb") as fileout:
                numbers = pickle.loads(recv_chunk)
                for num in numbers:
                    pickle.dump(num, fileout)

        # close connection
        generate_chunks.ChunkClass.connected_clients.remove(self.client_socket)
        self.client_socket.close()
        print("Client thread with ID %d quit" % self.client_id)
        print("Flag value:", generate_chunks.ChunkClass.generate_over)

        # if generate_over is True, send a sentinel in order to
        # automatically close the server accept state
        if generate_chunks.ChunkClass.generate_over == True and len(generate_chunks.ChunkClass.connected_clients) == 0:
            sentinel = CloseSentinel(self.settings)
            sentinel.sendCloseSignal()
