import socket
import threading

class RequestSentinel:
    lock = threading.Lock()
    sentinel_id = 0
    def __init__(self, address="127.0.1.1", port=5678):
        self.address = address
        self.port = port

def sendRequestSignal():
    # in case we have many clients connected to the server
    # we don't want all of them to send a sentinel
    # the listen thread is blocked on accept()
    RequestSentinel.lock.acquire()
    RequestSentinel.sentinel_id += 1

    if RequestSentinel.sentinel_id > 1:
        return

    aux_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    aux_socket.connect((self.address, self.port))
    aux_socket.send(b"SENTINEL_REQUEST_NEW_DATA")

    aux_socket.close()

    RequestSentinel.lock.release()

