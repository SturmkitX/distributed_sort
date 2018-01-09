from communications.comms import CommunicationProtocol

class LargeCommunicationProtocol:
    def __init__(self, sock, buffer_size=2):
        """
        Uses the CommunicationProtocol for transmitting large data across different communication nodes
        Wrapper implemented for convenience
        buffer_size is expressed in MegaBytes
        """
        self.communicator = CommunicationProtocol(sock)
        self.buffer_size = buffer_size * 1048576

    def sendMessage(self, file_path, delimiter=b"", chunk_end_message=b"CHUNK_END"):
        with open(file_path, "rb") as filein:
            while True:
                read_chunk = filein.read(self.buffer_size)
                if read_chunk == b"":
                    break
                self.communicator.sendMessage(read_chunk, delimiter) # 2MB of data
                self.communicator.receiveMessage(delimiter + b"_REQUEST")
        # it should enter this block when filein.read() fails
        self.communicator.sendMessage(chunk_end_message, delimiter)

    def receiveMessage(self, file_path, delimiter=b"", chunk_end_message=b"CHUNK_END"):
        numbers = bytearray()
        with open(file_path, "wb") as fileout:
            while True:
                received_sorted = self.communicator.receiveMessage(delimiter)
                if received_sorted == chunk_end_message:
                    break
                self.communicator.sendMessage(b"", delimiter + b"_REQUEST")
                numbers.extend(received_sorted)
                if len(numbers) > self.buffer_size:
                    fileout.write(numbers)
                    numbers = bytearray()
            fileout.write(numbers)

    def get_communicator(self):
        return self.communicator
