from multiprocessing import Process
from settings_parser import SettingsParser
from server_main import ServerClass

def start_server():
    settings = SettingsParser()
    settings.loadSettings("settings.cfg")
    server = ServerClass(settings)
    server.main()

if __name__ == "__main__":
    should_repeat = True
    while should_repeat:
        proc = Process(target=start_server)
        proc.start()

        proc.join()
        with open("server_exit_status.dat", "r") as filein:
            server_exit_status = filein.read()
            if "DO_NOT_REPEAT" in server_exit_status:
                should_repeat = False
                print("Shutting down server...")
            else:
                print("Restarting server...")
