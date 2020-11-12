
class Symbol:

    def __init__(self, name, type=None, dim=None) -> None:
        self.name = name
        self.type = type
        if dim is not None:
            self.dim = dim
        else:
            self.dim = []

    def num_of_dim(self):
        return len(self.dim)