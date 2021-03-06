import re


class Node:

    def __init__(self, line_number=None) -> None:
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

    def node_type(self):
        class_name = self.__class__.__name__
        return None if class_name == "Node" else re.match(r"([a-zA-Z]+)Node", class_name).group(1).lower()

    def get_all_children(self):
        all_children = [self]
        for child in self.children:
            all_children += child.get_all_children()
        return all_children

    def print_node(self, padding="", last_child=True):

        print(f"{padding}|-{self}")
        for child in self.children:
            if last_child:
                child.print_node(padding+"  ", child is self.children[-1])
            else:
                child.print_node(padding+"| ", child is self.children[-1])


    def print_tree(self):
        self.get_root().print_node()

    def __repr__(self) -> str:
        attributes = ""
        for attr, value in self.__dict__.items():
            if attr in ["parent", "children", "line_number", "scope"]:
                continue
            elif attr == "dims":
                if self.num_of_dims() > 0:
                    attributes += f' dims="{self.num_of_dims()}"'
            elif attr == "variable_list":
                attributes += f' variable_list={self.variable_list}'
            else:
                attributes += f' {attr}="{value}"'
        return f'{self.node_type()}{attributes}'

class ProgramNode(Node):
    
    def __init__(self, line_number=None):
        super().__init__(line_number=line_number)
        self.variable_list = []
        
    def set_address(self, name, address):
        all_children = self.get_all_children()
        all_variables = [node for node in all_children if node.node_type() == "variable" and 
                                                          node.name == name and
                                                          node.scope == self]
        for variable in all_variables:
            variable.address = address
        for variable in [var for var in self.variable_list if var.name == name]:
            variable.address = address

    def set_type(self, name, type):
        all_children = self.get_all_children()
        all_variables = [node for node in all_children if node.node_type() == "variable" and 
                                                          node.name == name and
                                                          node.scope == self]
        for variable in all_variables:
            variable.type = type
        for variable in self.variable_list:
            variable.type = type
    

class AssignNode(Node):
    
    def __init__(self, line_number=None, type=None) -> None:
        super().__init__(line_number=line_number)
        self.type = type  

class GoToNode(Node):
    pass

class VariableNode(Node):

    def __init__(self, name, type=None, dims=None, address=0, scope=None):
        super().__init__()
        self.name = name
        self.type = type
        self.address = address
        self.scope = scope
        if dims is not None:
            self.dims = dims
        else:
            self.dims = []

    def num_of_dims(self):
        return len(self.dims)

    def num_of_items(self):
        items = 1
        for dim in self.dims:
            items = items * dim
        return items

    def deepcopy(self):
        new_node = self.__class__(self.name)
        new_node.type = self.type
        new_node.dims = [dim for dim in self.dims]
        new_node.address = self.address
        new_node.scope = self.scope
        new_node.children = []

        return new_node

class LiteralNode(Node):

    def __init__(self, value) -> None:
        super().__init__()
        self.value = value
        self.set_type(value)
        self.address = None

    def set_type(self, value):
        if re.match(r"-?[0-9]+", value):
            self.type = "int"  
        elif re.match(r"-?[0-9]*\.[0-9]+", value):
            self.type = "float"
        elif re.match(r'".*"', value):
            self.type = "string"
        else:
            raise Exception(f"Literal {value} has no type.")

class OperatorNode(Node):
    
    def __init__(self, operation, type=None) -> None:
        super().__init__()
        self.operation = operation
        self.type = None

class ForNode(Node):
    pass

class IfNode(Node):
    pass

class SubRoutineNode(ProgramNode):
    pass

class PrintNode(Node):
    pass

class PrintlnNode(Node):
    pass

if __name__ == "__main__":
    main = Node("Aaron")
    child = Node("Blake")
    grandchild = Node("Cornell")

    main.add_child(Node("Duck"))
    main.add_child(Node("Elisa"))

    main.add_child(child)

    child.add_child(Node("Finn"))

    child.split_parent(Node("George"))

    main.add_child(Node("Heracles"))
    main.print_tree()
