import threading
import socket
from communications.comms import CommunicationProtocol
import pickle

class HandlerAdmin(threading.Thread):
    def __init__(self, sock, settings):
        threading.Thread.__init__(self)
        self.sock = sock
        self.settings = settings

    def run(self):
        communicator = CommunicationProtocol(self.sock)

        # get the admin credentials
        recv_cred = pickle.loads(communicator.receiveMessage(b"ADMIN_CREDENTIALS"))
        if recv_cred in self.settings.getValue("accepted_admins"):
            communicator.sendMessage(b"STATUS_OK", b"ADMIN_CREDENTIALS_STATUS")
        else:
            communicator.sendMessage(b"STATUS_INCORRECT", b"ADMIN_CREDENTIALS_STATUS")
            self.sock.close()
            return

        print("An administrator has connected.")

        while True:
            command = communicator.receiveMessage(b"ADMIN_COMMAND")

            if command == b"GET_SETTINGS":
                sets = dict()
                sets["sort_rule"] = self.settings.getValue("sort_rule")
                with open(sets["sort_rule"] + ".py", "rb") as filein:
                    sets["rule_data"] = filein.read()
                communicator.sendMessage(pickle.dumps(sets), b"COMMAND_PASSED")
            elif command == b"ADMIN_DISCONNECTED":
                break
        self.sock.close()
