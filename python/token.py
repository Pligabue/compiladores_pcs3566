
class Token:

    TYPES = {"identifier", "keyword", "separator", "operator", "literal", "comment"}

    def __init__(self, type=None, value=None) -> None:
        self.type = type
        self.value = value

    def set_type(self, type):
        if (type in self.TYPES):
            self.type = type
        else:
            print("Invalid type.\n")

    def __repr__(self) -> str:
        return f'<Token type={self.type} value="{self.value}">'