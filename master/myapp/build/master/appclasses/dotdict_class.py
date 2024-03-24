
class DotDict:
    """this class converts a dictionary to an object whose attributes can be accessed with dot notation"""
    def __init__(self, dictionary):
        self.dictionary = dictionary

    def __getattr__(self, item):
        if item in self.dictionary:
            return self.dictionary[item]
        else:
            raise AttributeError(f"'DotDict' object has no attribute '{item}'")
