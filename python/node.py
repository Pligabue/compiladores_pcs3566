
class Node:

    def __init__(self, type=None, line_number=None) -> None:
        self.type = type
        self.parent = None
        self.line_number = line_number
        self.children = []

    def is_root(self):
        return self.parent is None

    def add_child(self, node):
        self.children.append(node)
        node.parent = self

    def add_parent(self, node):
        node.add_child(self)

    def split_parent(self, node):
        if self.parent is not None:
            i = self.parent.children.index(self)
            self.parent.children[i] = node
            node.parent = self.parent
        self.add_parent(node)

    def replace_parent_with_self(self):
        if self.parent is None:
            return
        if self.parent.is_root():
            self.parent.children.remove(self)
            self.parent.parent = None
            self.parent = None
        else:
            grandparent = self.parent.parent
            i = grandparent.children.index(self.parent)
            grandparent.children[i] = self
            
            self.parent.children.remove(self)
            self.parent.parent = None

            self.parent = grandparent


    def has_type(self):
        return self.type is not None

    def has_siblings(self):
        if self.is_root():
            return False
        return len(self.parent.children) > 1

    def get_level(self):
        level = 0
        current_node = self
        while not current_node.is_root():
            current_node = current_node.parent
            level += 1

        return level

    def get_root(self):
        current_node = self
        while not current_node.is_root():
            current_node = current_node.parent
            
        return current_node

    def print_node(self, offset=2):
        print(f"type={self.type}")
        for child in self.children:
            print(" " * offset, end="")
            child.print_node(offset + 2)


    def print_tree(self):
        self.get_root().print_node()

    def __repr__(self) -> str:
        return f'<Node type={self.type}>'

if __name__ == "__main__":
    main = Node("Aaron")
    child = Node("Blake")
    grandchild = Node("Cornell")

    main.add_child(Node("Duck"))
    main.add_child(Node("Elisa"))

    main.add_child(child)

    child.add_child(Node("Finn"))

    child.split_parent(Node("George"))

    main.print_tree()
