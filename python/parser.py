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
            raise Exception(f'Invalid line number "{self.current_token.value}".\n')

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

    def build_expression_node(self, operators, operands):
        if len(operators) != len(operands)-1:
            raise Exception(f"Wrong number of operands. Operands = {operands}, operators = {operators}")
        if len(operators) <= 0:
            return operands[0]

        new_operators = []
        new_operands = []
        new_i = 0
        for i, operator in enumerate(operators):
            if operator.type == "*" or operator.type == "/":
                operator_node = operator
                left_node = operands[i]
                right_node = operands[i+1]
                operator_node.add_child(left_node)
                operator_node.add_child(right_node)
                if len(new_operands) <= new_i:
                    new_operands.append(operator_node)
                else:
                    new_operands[new_i] = operator_node
                operands[i+1] = operator_node
            else:
                new_operators.append(operator)
                new_operands.append(operands[i])
                new_i += 1
                if operator == operators[-1]:
                    new_operands.append(operands[i+1])
            i += 1
        
        print(new_operators)
        print(new_operands)

        acc_node = new_operands[0]
        for i, operator in enumerate(new_operators):
            operator_node = operator
            right_node = new_operands[i+1]
            operator_node.add_child(acc_node)
            operator_node.add_child(right_node)
            acc_node = operator_node

        return acc_node

    def handle_expression(self):
        operands = []
        operators = []
        
        while True:
            if self.current_token.type == "identifier":
                id_node = self.handle_identifier(is_assignment=False)
                operands.append(id_node)
            elif self.current_token.type == "literal":
                literal_node = Node(self.current_token.value)
                operands.append(literal_node)
                self.get_next_token()
            elif self.current_token.type == "separator" and self.current_token.value == "(":
                self.get_next_token()
                subexpression_node = self.handle_expression()
                operands.append(subexpression_node)
            else:
                break

            if self.current_token.type == "operator":
                operator_node = Node(self.current_token.value)
                operators.append(operator_node)
                self.get_next_token()
            else:
                if self.current_token.type == "separator" and self.current_token.value == ")":
                    self.get_next_token()
                break
        return self.build_expression_node(operators, operands)

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