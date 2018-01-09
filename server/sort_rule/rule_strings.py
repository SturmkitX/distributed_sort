# imports required by class
import random
import pickle
import string

class ElementUnit:
    def __init__(self, string):
        self.string = string

    def __lt__(self, other):
        return self.string[len(self.string) // 2] < other.string[len(self.string) // 2]

    def __eq__(self, other):
        return self.string[len(self.string) // 2] == other.string[len(self.string) // 2]

    def representation(self):
        # send it as a string, as we need to write it as a string in the file
        # it can be changed, but it must match the type required during
        # the merge process
        return self.string

    def get_random_sequence(count):
        """
        Returns a random sequence of <count> elements, represented as a byte array
        """
        string_list = bytearray()
        for i in range(count):
            current = "".join(random.choice(string.ascii_uppercase) for _ in range(15))
            num = pickle.dumps(ElementUnit(current))
            string_list.extend(num)
        return string_list
