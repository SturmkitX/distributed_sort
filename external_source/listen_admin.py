import threading
import socket
from handler_admin import HandlerAdmin

class ListenerAdmin(threading.Thread):
    def __init__(self, sock, settings):
        threading.Thread.__init__(self)
        self.sock = sock
        self.settings = settings
        self.connected_admins = []

    def run(self):
        while True:
            client_sock, client_addr = self.sock.accept()

            handler = HandlerAdmin(client_sock, self.settings)
            self.connected_admins.append((handler, client_sock))

            handler.start()

            for field in self.connected_admins:
                if not field[0].is_alive():
                    self.connected_admins.remove(field)
