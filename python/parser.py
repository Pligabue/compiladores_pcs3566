from symbol import Symbol
import symbol
from lexical_analyser import LexicalAnalyser
from node import Node

def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

class Parser:

    TYPES = {"program", "assign", "read", "data", "print", "goto", "if", "for", 
             "next", "dim", "def", "gosub", "return", "remark", "+", "-", "*", "/"}

    def __init__(self, filename="sample_text.txt") -> None:
        self.current_token_index = 0
        self.token_list = LexicalAnalyser(filename).analyse_text()
        self.current_token = self.token_list[0]
        self.root = Node("program")
        self.current_node = self.root
        self.parentheses_count = 0
        self.current_line_number = 0
        self.symbol_list = []

    def get_next_token(self):
        self.current_token_index += 1
        if (self.current_token_index < len(self.token_list)):
            self.current_token = self.token_list[self.current_token_index]

    def peek_next_token(self):
        if (self.current_token_index + 1 < len(self.token_list)):
            return self.token_list[self.current_token_index + 1]
        return None

    def get_previous_token(self):
        self.current_token_index -= 1
        if (self.current_token_index >= 0):
            self.current_token = self.token_list[self.current_token_index]

    def build_ast(self):
        while self.current_token_index < len(self.token_list):
            self.set_line_number()
            self.handle_keyword(self.current_token.value)
        return self.root

    def set_line_number(self):
        try:
            self.current_line_number = int(self.current_token.value)
            self.get_next_token()
        except:
            raise Exception("Invalid line number.\n")

    def handle_keyword(self, keyword):

        if keyword == "LET":                
            assign_node = Node("assign")
            assign_node.line_number = self.current_line_number
            self.current_node.add_child(assign_node)

            self.get_next_token()
            token_type = self.current_token.type
            token_value = self.current_token.value

            id_node = self.handle_identifier()
            assign_node.add_child(id_node)

            token_type = self.current_token.type
            token_value = self.current_token.value


            if token_type != "operator" or token_value != "=":
                print(token_type)
                print(token_value)
                raise Exception("Assignment must have equals sign.\n")

            self.get_next_token()
            expression_node = self.handle_expression()   
            assign_node.add_child(expression_node)

        elif keyword == "DIM":

            self.get_next_token()
            if self.current_token.type != "identifier":
                raise Exception("Dimention must get an identifier.")
            id_name = self.current_token.value
            self.get_next_token()
            dim = []
            while self.current_token.type == "separator" and self.current_token.value == "[":
                self.get_next_token()
                if self.current_token.type == "literal" and is_int(self.current_token.value):
                    dim.append(int(self.current_token.value))
                else:
                    raise Exception("Index must be integer.")
                self.get_next_token()
                if self.current_token.type != "separator" or self.current_token.value != "]":
                    raise Exception("Must close brackets")
                self.get_next_token()
            self.symbol_list.append(Symbol(id_name, dim=dim))
            
        else:
            return

    def handle_expression(self):
        expression_node = self.get_expressions()
        if self.parentheses_count > 0:
            raise Exception("Parentheses error.\n")
        return expression_node

    def get_expressions(self):

        main_node = Node()
        temp_node = main_node
        automaton_done = False
        state = 0

        while not automaton_done:    
            if state == 0:
                if self.current_token.type == "identifier":
                    main_node.type = self.current_token.value
                    if main_node.has_siblings():
                        main_node = main_node.parent
                    state = 1
                elif self.current_token.type == "literal":
                    main_node.type = self.current_token.value
                    if main_node.has_siblings():
                        main_node = main_node.parent
                    state = 1
                elif self.current_token.type == "separator" and self.current_token.value == "(":
                    self.parentheses_count += 1
                    temp_node = Node()
                    main_node.add_child(temp_node)
                    main_node = temp_node
                    state = 2
                else:
                    raise Exception("Must be assigned to something.\n")
            
            elif state == 1:
                if self.current_token.type == "operator":
                    temp_node = Node(self.current_token.value)
                    main_node.split_parent(temp_node)

                    main_node = Node()
                    temp_node.add_child(main_node)

                    state = 0
                else:
                    automaton_done = True
            
            elif state == 2:
                if self.current_token.type == "identifier":
                    main_node.type == self.current_token.value
                    if main_node.has_siblings():
                        main_node = main_node.parent
                    state = 3
                elif self.current_token.type == "literal":
                    main_node.type == self.current_token.value
                    if main_node.has_siblings():
                        main_node = main_node.parent
                    state = 3
                elif self.current_token.type == "separator" and self.current_token.value == "(":
                    self.parentheses_count += 1
                    temp_node = Node()
                    main_node.add_child(temp_node)
                    main_node = temp_node

                    state = 2
                else:
                    raise Exception("Must be assigned to something.\n")
        
            elif state == 3:
                if self.current_token.type == "operator":
                    temp_node = Node(self.current_token.value)
                    main_node.split_parent(temp_node)

                    main_node = Node()
                    temp_node.add_child(main_node)

                    state = 2
                elif self.current_token.type == "separator" and self.current_token.value == ")":
                    self.parentheses_count -= 1
                    temp_node = main_node.parent
                    if temp_node.type is not None:
                        main_node.replace_parent_with_self()
                    else:
                        main_node = temp_node

                    if self.parentheses_count == 0:
                        state = 1
                else:
                    raise Exception("Expected operator or closing parenthesis")
            else:
                raise Exception("Invalid state.")
              
            if not automaton_done:
                self.get_next_token() 
          
        return main_node.get_root()

    def get_symbol(self, name):
        for symbol in self.symbol_list:
            if symbol.name == name:
                return symbol
        return None

    def list_contains_symbol(self, name):
        for symbol in self.symbol_list:
            if symbol.name == name:
                return True
        return False

    def handle_identifier(self, is_assignment=True):
        id_node = Node()
        if self.current_token.type == "identifier":
            id_name = self.current_token.value
            id_node.type = id_name

            if not self.list_contains_symbol(id_name):
                self.symbol_list.append(Symbol(id_name)) 

            self.get_next_token() 
            dim = 0
            while self.current_token.type == "separator" and self.current_token.value == "[":
                self.get_next_token()
                dim += 1

                expression_node = self.handle_expression()
                id_node.add_child(expression_node)
                if self.current_token.type == "separator" and self.current_token.value == "]":
                    self.get_next_token()
                else:
                    raise Exception("Wrong index.")  
            if self.get_symbol(id_name).num_of_dim() != dim:
                raise Exception(f"Wrong dimensions. The variable {id_name} has {self.get_symbol(id_name).num_of_dim()} dimentions.")
        else:
            raise Exception("Must assign to variable.")
        return id_node

if __name__ == "__main__":
    ast = Parser().build_ast()
    ast.print_tree()