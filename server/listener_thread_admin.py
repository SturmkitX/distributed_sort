# The connections listening thread

import socket
import threading
import handler_thread_admin
import sys

class ListenThreadAdmin(threading.Thread):
    def __init__(self, listen_socket, settings):
        threading.Thread.__init__(self)
        self.listen_socket = listen_socket
        self.settings = settings
        self.connected_admins = []

    def run(self):
        while True:
            (admin_socket, address) = self.listen_socket.accept()
            newConn = handler_thread_admin.HandlerThreadAdmin(admin_socket, address, self.settings)

            self.connected_admins.append((admin_socket, newConn))
            newConn.start()

            for field in self.connected_admins:
                if not field[1].is_alive():
                    self.connected_admins.remove(field)
