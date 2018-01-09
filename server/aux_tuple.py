class AuxiliaryTuple:
    def __init__(self, element, file_descriptor):
        self.element = element
        self.fd = file_descriptor

    def __lt__(self, other):
        return self.element < other.element

    def __eq__(self, other):
        return self.element == other.element

    def __gt__(self, other):
        return self.element > other.element

    def representation(self):
        return self.element.representation()

