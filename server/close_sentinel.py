import socket
import threading
from communications.comms import CommunicationProtocol

class CloseSentinel:
    lock = threading.Lock()
    close_flag = False
    # sentinel_id = 0
    def __init__(self, settings):
        self.settings = settings

    def sendCloseSignal(self):
        # in case we have many clients connected to the server
        # we don't want all of them to send a sentinel
        # the listen thread is blocked on accept()
        # the function is only called when the last client has disconnected, apparently
        aux_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        aux_socket.connect((socket.gethostname(), int(self.settings.getValue("server_port"))))
        communicator = CommunicationProtocol(aux_socket)
        communicator.sendMessage(b"SENTINEL_CLOSE_SERVER", b"CLIENT_TYPE")

        aux_socket.close()

    def sendRestartSignal(self):
        aux_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        aux_socket.connect((socket.gethostname(), int(self.settings.getValue("server_port"))))
        communicator = CommunicationProtocol(aux_socket)
        communicator.sendMessage(b"SENTINEL_RESTART_SERVER", b"CLIENT_TYPE")

        aux_socket.close()

    def sendShutdownSignal(self):
        aux_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        aux_socket.connect((socket.gethostname(), int(self.settings.getValue("server_port"))))
        communicator = CommunicationProtocol(aux_socket)
        communicator.sendMessage(b"SENTINEL_SHUTDOWN_SERVER", b"CLIENT_TYPE")

        aux_socket.close()
