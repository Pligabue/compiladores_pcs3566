from lexical_analyser import LexicalAnalyser
from node import ForNode, GoToNode, OperatorNode, ProgramNode, AssignNode, LiteralNode, SubRoutineNode, VariableNode

from helpers import is_int

class Parser:

    TYPES = {"program", "assign", "read", "data", "print", "goto", "if", "for", 
             "next", "dim", "def", "gosub", "return", "remark", "+", "-", "*", "/"}

    def __init__(self, filename="sample_text.txt") -> None:
        self.current_token_index = 0
        self.token_list = LexicalAnalyser(filename).analyse_text()
        self.current_token = self.token_list[0]
        self.root = ProgramNode()
        self.current_node = self.root
        self.parentheses_count = 0
        self.current_line_number = 0
        self.text_line = 1
        self.variable_list = []
        self.scope_stack = [self.root]

    def tokens_remaining(self):
        return self.current_token_index < len(self.token_list)

    def get_next_token(self):
        self.current_token_index += 1
        if self.tokens_remaining():
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
            if self.tokens_remaining() and self.current_token.value != "\n":
                raise Exception(f"Command must end with a new line. Ended with {self.current_token.value}.")
            else:
                self.get_next_token()
        return self.root

    def set_line_number(self):
        if is_int(self.current_token.value):
            self.text_line += 1
            self.current_line_number = int(self.current_token.value)
            self.get_next_token()
        else:
            raise Exception(f'Invalid line number "{self.current_token.value}" on line {self.text_line}.\n')

    def handle_keyword(self, keyword):

        if keyword == "LET":
            self.LET()
        elif keyword == "DIM":
            self.DIM()
        elif keyword == "GOTO":
            self.GOTO()
        elif keyword == "FOR":
            self.FOR()
        elif keyword == "END":
            self.END()
        elif self.current_token.type == "identifier":
            self.LET(with_keyword=False)
        else:
            raise Exception(f"Invalid command at line {self.text_line}.")

    def LET(self, with_keyword=True):                
        assign_node = AssignNode()
        assign_node.line_number = self.current_line_number
        self.current_node.add_child(assign_node)

        if with_keyword:
            self.get_next_token()
        token_type = self.current_token.type
        token_value = self.current_token.value

        id_node = self.handle_identifier(being_assigned=True)
        assign_node.add_child(id_node)

        token_type = self.current_token.type
        token_value = self.current_token.value


        if token_type != "operator" or token_value != "=":
            raise Exception("Assignment must have equals sign.\n")

        self.get_next_token()
        expression_node = self.handle_expression()   
        assign_node.add_child(expression_node)

        assign_node.type = expression_node.type
        if id_node.type is None:
            id_node.type = expression_node.type
        elif id_node.type != expression_node.type:
            raise Exception("Assigned and expression have different types.")

            
    def DIM(self):
        self.get_next_token()

        if self.current_token.type != "identifier":
            raise Exception("Dimention must get an identifier.")
        id_name = self.current_token.value

        self.get_next_token()
        dims = []
        while self.current_token.type == "separator" and self.current_token.value == "[":
            self.get_next_token()
            if self.current_token.type == "literal" and is_int(self.current_token.value):
                dims.append(int(self.current_token.value))
            else:
                raise Exception("Index must be integer.")
            self.get_next_token()
            if self.current_token.type != "separator" or self.current_token.value != "]":
                raise Exception("Must close brackets")
            self.get_next_token()

        self.variable_list.append(VariableNode(id_name, dims=dims))

    def GOTO(self):
        goto_node = GoToNode()
        goto_node.line_number = self.current_line_number
        self.current_node.add_child(goto_node)

        self.get_next_token()
        if self.current_token.type == "literal" and is_int(self.current_token.value):
            goto_node.add_child(LiteralNode(self.current_token.value))
            self.get_next_token()
        else:
            raise Exception(f"GOTO command must have an integer as argument. Received {self.current_token.value}")

    def FOR(self):
        for_node = ForNode()
        for_node.line_number = self.current_line_number
        self.current_node.add_child(for_node)

        self.get_next_token()
        self.current_node = for_node
        self.LET(with_keyword=False)

        if self.current_token.type != "keyword" or self.current_token.value != "TO":
            raise Exception(f"FOR loop requires a final value, indicated by the TO keyword. Received {self.current_token.value}.")
        
        self.get_next_token()
        limit_node = self.handle_expression()
        for_node.add_child(limit_node)

        if self.current_token.type == "keyword" and self.current_token.value == "STEP":
            self.get_next_token()
            step_node = self.handle_expression()
        elif self.current_token.type == "separator" and self.current_token.value == "\n":
            step_node = LiteralNode("1")
        else:
            raise Exception(f"FOR loop must end with STEP or a new line. Received {self.current_token.value}")

        for_node.add_child(step_node)

        subroutine_node = SubRoutineNode()
        for_node.add_child(subroutine_node)
        self.scope_stack.append(subroutine_node)
        self.current_node = subroutine_node

    def END(self):
        if len(self.scope_stack) <= 1:
            raise Exception(f"END keyword cannot be used at the global scope.")
        else:
            self.scope_stack.pop()
            self.current_node = self.scope_stack[-1]
        self.get_next_token()

    def get_operation_type(self, left_node, right_node):
        types = left_node.type, right_node.type
        if types[0] is None or types[1] is None:
            raise Exception("Operands must have a type. Check if any variables are uninitialized.")

        if types[0] == "int" or types[1] == "int":
            return "int"
        elif types[0] == "float" and types[1] == "float":
            return "float"
        elif types[0] == "string" and types[1] == "string":
            return "string"
        else:
            raise Exception("Operands hava incompatible types.")

    def build_expression_node(self, operators, operands):
        if len(operators) != len(operands)-1:
            raise Exception(f"Wrong number of operands. Operands = {operands}, operators = {operators}")
        if len(operators) <= 0:
            return operands[0]

        new_operators = []
        new_operands = []
        new_i = 0
        for i, operator in enumerate(operators):
            if operator.operation == "*" or operator.operation == "/":
                operator_node = operator
                left_node = operands[i]
                right_node = operands[i+1]
                operator_node.add_child(left_node)
                operator_node.add_child(right_node)
                operator_node.type = self.get_operation_type(left_node, right_node)
                if new_i >= len(new_operands):
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

        acc_node = new_operands[0]
        for i, operator in enumerate(new_operators):
            operator_node = operator
            right_node = new_operands[i+1]
            operator_node.add_child(acc_node)
            operator_node.add_child(right_node)
            operator_node.type = self.get_operation_type(acc_node, right_node)
            acc_node = operator_node

        return acc_node

    def handle_expression(self):
        operands = []
        operators = []
        
        while True:
            if self.current_token.type == "identifier":
                id_node = self.handle_identifier(being_assigned=False)
                operands.append(id_node)
            elif self.current_token.type == "literal":
                literal_node = LiteralNode(self.current_token.value)
                operands.append(literal_node)
                self.get_next_token()
            elif self.current_token.type == "separator" and self.current_token.value == "(":
                self.get_next_token()
                subexpression_node = self.handle_expression()
                self.get_next_token()
                operands.append(subexpression_node)
            else:
                break

            if self.current_token.type == "operator":
                operator_node = OperatorNode(self.current_token.value)
                operators.append(operator_node)
                self.get_next_token()
            elif self.current_token.type == "separator" or self.current_token.type == "keyword":
                break
            else:
                raise Exception(f"Expressions must have either operators or separators. Received {self.current_token.value}")
        return self.build_expression_node(operators, operands)

    def get_symbol(self, name):
        for symbol in self.variable_list:
            if symbol.name == name:
                return symbol
        return None

    def get_variable_by_name(self, variable_name):
        for variable_node in self.variable_list:
            if variable_node.name == variable_name:
                return variable_node
        return None

    def list_contains_symbol(self, variable_name):
        return self.get_variable_by_name(variable_name) is not None

    def handle_identifier(self, being_assigned=True):

        if self.current_token.type == "identifier":

            id_node = self.get_variable_by_name(self.current_token.value)
            if id_node is None:
                if being_assigned:
                    id_node = VariableNode(self.current_token.value, dims=[])
                    self.variable_list.append(id_node)
                else:
                    raise Exception(f"Variable {self.current_token.value} is not initialized.")

            self.get_next_token() 
            dim = 0
            while self.current_token.type == "separator" and self.current_token.value == "[":
                dim += 1

                self.get_next_token()
                expression_node = self.handle_expression()
                id_node.add_child(expression_node)

                if self.current_token.type == "separator" and self.current_token.value == "]":
                    self.get_next_token()
                else:
                    raise Exception("Wrong index.")  
            
            if id_node.num_of_dims() != dim:
                raise Exception(f"Wrong dimensions. The variable {id_node.name} has {id_node.num_of_dims()} dimentions, not {dim}.")
        else:
            raise Exception("Must assign to variable.")
        return id_node

if __name__ == "__main__":
    ast = Parser().build_ast()
    ast.print_tree()