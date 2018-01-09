# imports required by class
import random
import pickle

class ElementUnit:
    def __init__(self, number):
        self.number = number

    def __lt__(self, other):
        return self.number < other.number

    def __eq__(self, other):
        return self.number == other.number

    def representation(self):
        # send it as a string, as we need to write it as a string in the file
        # it can be changed, but it must match the type required during
        # the merge process
        return str(self.number)

    def get_random_sequence(count):
        """
        Returns a random sequence of <count> elements, represented as a byte array
        """
        numbers = bytearray()
        for i in range(count):
            num = pickle.dumps(ElementUnit(random.randint(0, 2000000)))
            numbers.extend(num)
        return numbers
