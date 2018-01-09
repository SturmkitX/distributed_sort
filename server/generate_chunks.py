# generate fixed length chunks
# this file is specific for arbitrary-length numbers with sizes specified on 4 bytes
# this may be changed, but right now it is for testing purposes

# LZMA compression should be added

import threading
import pickle

class ChunkClass:
    chunks = None #open("numbers_test", "rb")
    chunk_number = 0
    chunks_received = 0
    lock = threading.Lock()
    generate_over = False
    connected_clients = []


def get_chunk():
    ChunkClass.lock.acquire()

    # get a list of 4096 numbers
    number_list = []
    for i in range(4096):
        try:
            num = pickle.load(ChunkClass.chunks)
            number_list.append(num)
        except (pickle.UnpicklingError, EOFError):
            break
    ChunkClass.lock.release()

    if len(number_list) == 0:
        ChunkClass.generate_over = True
        return (-1, None)
    ChunkClass.chunk_number += 1
    return (ChunkClass.chunk_number, number_list)

def increment_received():
    ChunkClass.lock.acquire()

    ChunkClass.chunks_received += 1

    ChunkClass.lock.release()
