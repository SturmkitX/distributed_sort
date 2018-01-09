import hashlib
import socket

class CommunicationProtocol:
    def __init__(self, sock):
        self.sock = sock

    def receiveMessage(self, delimiter=None, progress=False, progress_delta=5):
        # receive the md5 hash
        # TODO: decompress using LZMA
        md5hash = self.sock.recv(16)
        msg_len = int.from_bytes(self.sock.recv(4), "little")
        chunks = bytearray()
        delim_len = 0
        last_progress = 0

        recv_chunk = self.sock.recv(4096)
        recv_size = len(recv_chunk)
        chunks.extend(recv_chunk)
        if delimiter is not None:
            delim_len = len(delimiter)
            while recv_chunk[-delim_len:] != delimiter:
                recv_chunk = self.sock.recv(4096)
                chunks.extend(recv_chunk)
                recv_size = len(chunks)
                actual_progress = (recv_size * 100) / msg_len
                if progress == True and actual_progress - last_progress >= progress_delta:
                    print("Receive message progress:", actual_progress, "%")
                    last_progress = actual_progress
        if hashlib.md5(chunks).digest() != md5hash:
            print("DEBUG: Received MD5 hash is incorrect")
            print(chunks)
            return None

        return chunks[:-delim_len]

    def sendMessage(self, message, delimiter=None, progress=False):
        # limit transfer rate to 4 MB/s (1 4096 byte chunk every 1 ms)
        # TODO: compress using LZMA

        if delimiter is not None:
            message += delimiter
        msg_len = len(message)
        md5hash = hashlib.md5(message).digest()
        self.sock.send(md5hash)
        self.sock.send(msg_len.to_bytes(4, "little"))

        # in case the message is too long
        sent_len = 0
        while sent_len < msg_len:
            sent_len += self.sock.send(message[sent_len:])
            if progress == True:
                print("Sent percentage:", (sent_len * 100) / msg_len, "%")
