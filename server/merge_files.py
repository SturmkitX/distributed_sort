import heapq
import pickle
from aux_tuple import AuxiliaryTuple
import generate_chunks
import os
import importlib

# ElementUnit = None

class MergeClass:
    def __init__(self, settings):
        # module = importlib.import_module(settings.getValue("sort_rule"))
        # global ElementUnit
        # ElementUnit = module.ElementUnit
        pass

    def merge_sorted(self, filenames, interm_chunk):
        open_files = []
        # print(generate_chunks.ChunkClass.chunk_number)
        for fn in filenames:
            fd = open("chunks/%s" % fn, "rb")
            open_files.append(fd)
        outfile = open("chunks/interm_chunk_%d" % interm_chunk, "wb")
        print("Files open for merging:", filenames)
        print("File open for output: interm_chunk_%d" % interm_chunk)

        # create the heap
        heap = []

        # add the initial values into the heap
        # each value is a tuple (value, file_number)
        for fd in open_files:
            heapq.heappush(heap, AuxiliaryTuple(pickle.load(fd), fd))

        # remove the top element, add a new one, until the heap becomes empty
        while len(heap) > 0:
            extracted = heapq.heappop(heap)
            pickle.dump(extracted.element, outfile)

            fd = extracted.fd
            # print("Read file:", file_read)
            try:
                heapq.heappush(heap, AuxiliaryTuple(pickle.load(fd), fd))
            except (pickle.UnpicklingError, EOFError):
                fd.close()
                open_files.remove(fd)

        outfile.close()

    def merge_final(self):
        # there may be too many chunks available, and we cannot open that many files
        # open file handles limit on linux : 1024; on windows: 512 (including stdin, stdout, stderr)
        # they may be changed using root privileges, but we intend to run the application without root privileges

        # first, get the list of files inside "chunks/"
        # the walk function returns recursively the list of files and directories inside the given dir, but we are only interested in the toplevel
        # no man should manually change the chunks folder!
        generated_files = []
        for (_, _, filenames) in os.walk("chunks/"):
            generated_files.extend(filenames)
            break # just to be sure
        interm_chunk = 0
        while len(generated_files) > 1:
            interm_chunk += 1
            num_chunks = min(len(generated_files), 256)
            self.merge_sorted(generated_files[:num_chunks], interm_chunk)
            for fn in generated_files[:num_chunks]:
                os.unlink("chunks/%s" % fn)
            generated_files[:num_chunks] = []
            generated_files.append("interm_chunk_%d" % interm_chunk)

        # there is only one open file now, with all its elements pickled
        # write these elements in text format to merged_final
        with open("merged_final", "w") as fileout:
            try:
                with open("chunks/interm_chunk_%d" % interm_chunk, "rb") as filein:
                    while True:
                        fileout.write(pickle.load(filein).representation() + "\n")
            except (pickle.UnpicklingError, EOFError):
                pass
        return "chunks/interm_chunk_%d" % interm_chunk

if __name__ == "__main__":
    merger = MergeClass()
    merger.merge_final()
