# Main module for client

import socket
import os
import pickle
from communications.comms import CommunicationProtocol
from settings_parser import SettingsParser
from client_handler_thread import ClientHandlerThread

class ClientClass:
    def __init__(self, settings):
        self.running_threads = []
        self.settings = settings

    def main(self):
        # print(settings.settings)
        # print(settings.getValue("available_cpus"))

        for i in range(1, int(settings.getValue("available_cpus")) + 1):
            actual_thread = ClientHandlerThread(settings, i)
            actual_thread.start()
            self.running_threads.append(actual_thread)

        for thr in self.running_threads:
            thr.join()

if __name__ == "__main__":
    settings = SettingsParser()
    settings.loadSettings("settings.cfg")
    client = ClientClass(settings)
    client.main()
