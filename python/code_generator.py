from node import IfNode
from syntax_analyser import SyntaxAnalyser

import sys

class CodeGenerator:

    def __init__(self, filename="./sample_text.txt") -> None:
        self.filename = filename
        self.program_lines = []
        self.relative_address = 0
        self.setup()
    
    def setup(self):
        syntax_analyser = SyntaxAnalyser(filename=self.filename)
        self.ast = syntax_analyser.build_ast()
        self.error_list = syntax_analyser.error_list
        self.all_strings = ""
        for string in syntax_analyser.string_list:
            self.all_strings += string.address + ":\n"
            string_value = string.value[:-1] + "\\0\""
            self.all_strings += f"\t.ascii\t{string_value}\n"

    def run(self):
        if self.ast.node_type() != "program":
            raise Exception(f"Root node must be a program node.")

        program_node = self.ast

        self.build_overhead()

        self.set_scope_variables_address(program_node)

        for child_node in program_node.children:
            self.generate_code(child_node)

        self.build_tail()

        self.ast.print_tree()
        for e, line_number in self.error_list:
            print(f"At line {line_number}:", e)

        f = open(f"final.s", "w")
        f.write("\n".join(self.program_lines) + "\n")
        f.close()

    def set_scope_variables_address(self, routine_node):
        prev_relative_address = self.relative_address
        for variable_node in routine_node.variable_list:
            if variable_node.type == "int":
                self.relative_address += 4 * variable_node.num_of_items()
            routine_node.set_address(variable_node.name, self.relative_address)
        self.program_lines.append(f"\tsubl\t${self.relative_address-prev_relative_address},\t%esp")
        
    def generate_code(self, node):
        if node.node_type() == "assign":
            self.generate_assign(node)
        elif node.node_type() in ["print", "println"]:
            self.generate_print(node)
        elif node.node_type() == "for":
            self.generate_for(node)
        elif node.node_type() == "if":
            self.generate_if(node)
        elif node.node_type() == "read":
            self.generate_read(node)

    def generate_assign(self, node):
        variable_node = node.children[0]
        expression_node = node.children[1]
        self.generate_expression(expression_node)
        n_dims = variable_node.num_of_dims()
        if n_dims != 0:
            for n_dim in range(n_dims):
                n_index_node = variable_node.children[n_dim]
                self.generate_expression(n_index_node)
            offset = 1
            self.program_lines.append(f"\tmovl\t$0,\t%edx")
            for dim in variable_node.dims[::-1]:
                self.program_lines.append(f"\tpopl\t%eax")
                self.program_lines.append(f"\timul\t${offset},\t%eax")
                self.program_lines.append(f"\taddl\t%eax,\t%edx")
                offset = offset * dim
            self.program_lines.append(f"\tpopl\t%eax")
            self.program_lines.append(f"\tmovl\t%eax,\t-{variable_node.address}(%ebp, %edx, 4)")
        else:
            self.program_lines.append(f"\tpopl\t%eax")
            self.program_lines.append(f"\tmovl\t%eax,\t-{variable_node.address}(%ebp)")

    def generate_for(self, for_node):
        assign_node = for_node.children[0]
        variable_node = assign_node.children[0]
        limit_node = for_node.children[1]
        step_node = for_node.children[2]
        subroutine_node = for_node.children[3]

        self.generate_assign(assign_node)
        self.program_lines.append(f"\tjmp\tFOR_{for_node.line_number}_END")
        self.program_lines.append(f"FOR_{for_node.line_number}_START:")
        
        self.set_scope_variables_address(subroutine_node)
        for child_node in subroutine_node.children:
            self.generate_code(child_node)

        self.program_lines.append(f"\taddl\t${step_node.value},\t-{variable_node.address}(%ebp)")
        self.program_lines.append(f"FOR_{for_node.line_number}_END:")

        self.generate_expression(limit_node)
        self.program_lines.append(f"\tpopl\t%eax")
        self.program_lines.append(f"\tcmpl\t%eax,\t-{variable_node.address}(%ebp)")
        self.program_lines.append(f"\tjle\tFOR_{for_node.line_number}_START")

    def generate_if(self, if_node):
        comparator_node = if_node.children[0]
        true_node = if_node.children[1]
        if len(if_node.children) > 2:
            false_node = if_node.children[2]
            destination = f"ELSE_{if_node.line_number}"
        else:
            false_node = None
            destination = f"END_{if_node.line_number}"

        left_node = comparator_node.children[0]
        right_node = comparator_node.children[1]
        self.generate_expression(left_node)
        self.generate_expression(right_node)
        self.program_lines.append(f"\tpopl\t%eax")
        self.program_lines.append(f"\tpopl\t%edx")

        if comparator_node.operation == "==":
            jump = "jne"
        elif comparator_node.operation == "<":
            jump = "jg"
            self.program_lines.append(f"\tsubl\t$1,\t%eax")
        elif comparator_node.operation == "<=":
            jump = "jg"
        elif comparator_node.operation == ">":
            jump = "jle"
        elif comparator_node.operation == ">=":
            jump = "jle"
            self.program_lines.append(f"\tsubl\t$1,\t%eax")
        elif comparator_node.operation == "<>":
            jump = "je"
        else:
            raise Exception(f"Expected comparator. Received {comparator_node.value}.")

        self.program_lines.append(f"\tcmpl\t%eax,\t%edx")
        self.program_lines.append(f"\t{jump}\t{destination}")

        for child_node in true_node.children:
            self.generate_code(child_node)
        self.program_lines.append(f"\tjmp\tEND_{if_node.line_number}")

        if false_node is not None:
            self.program_lines.append(f"ELSE_{if_node.line_number}:")
            for child_node in false_node.children:
                self.generate_code(child_node)

        self.program_lines.append(f"END_{if_node.line_number}:")

    def generate_expression(self, expression_node):
        if expression_node.node_type() == "literal":
            self.program_lines.append(f"\tpushl\t${expression_node.value}")

        elif expression_node.node_type() == "variable":
            n_dims = expression_node.num_of_dims()
            if n_dims != 0:
                for n_dim in range(n_dims):
                    n_index_node = expression_node.children[n_dim]
                    self.generate_expression(n_index_node)

                offset = 1
                self.program_lines.append(f"\tmovl\t$0,\t%edx")
                for dim in expression_node.dims[::-1]:
                    self.program_lines.append(f"\tpopl\t%eax")
                    self.program_lines.append(f"\timul\t${offset},\t%eax")
                    self.program_lines.append(f"\taddl\t%eax,\t%edx")
                    offset = offset * dim
                self.program_lines.append(f"\tpushl\t-{expression_node.address}(%ebp, %edx, 4)")
            else:
                self.program_lines.append(f"\tpushl\t-{expression_node.address}(%ebp)")

        elif expression_node.node_type() == "operator":

            left_node = expression_node.children[0]
            right_node = expression_node.children[1]
            self.generate_expression(left_node)
            self.generate_expression(right_node)
            self.program_lines.append(f"\tpopl\t%edx")
            self.program_lines.append(f"\tpopl\t%eax")

            operations = {
                "+": "addl",
                "-": "subl",
                "*": "imul",
                "/": "divl",
                "^": "pow"
            }
            try:
                operation = operations[expression_node.operation]
            except KeyError as e:
                raise Exception(f"Operator {expression_node.operation} doesn't exist.")

            if operation == "idivl":
                self.program_lines.append(f"\tmovl\t%edx,\t%ecx")
                self.program_lines.append(f"\tcltd")
                self.program_lines.append(f"\tidivl\t%ecx")
                self.program_lines.append(f"\tpushl\t%eax")
            elif operation == "pow":
                self.program_lines.append(f"\tmovl\t$1,\t%ecx")
                self.program_lines.append(f"POW_{expression_node.get_node_position()}_START:")
                self.program_lines.append(f"\tcmpl\t$0,\t%edx")
                self.program_lines.append(f"\tjle\tPOW_{expression_node.get_node_position()}_END")
                self.program_lines.append(f"\tsubl\t$1,\t%edx")
                self.program_lines.append(f"\timul\t%eax,\t%ecx")
                self.program_lines.append(f"\tjmp\tPOW_{expression_node.get_node_position()}_START")
                self.program_lines.append(f"POW_{expression_node.get_node_position()}_END:")
                self.program_lines.append(f"\tpushl\t%ecx")
            else:
                self.program_lines.append(f"\t{operation}\t%edx,\t%eax")
                self.program_lines.append(f"\tpushl\t%eax")

    def generate_print(self, print_node):

        for child_node in print_node.children[::-1]:
            if child_node == print_node.children[0]:
                self.program_lines.append(f"\tpushl\t${child_node.address}")
            else:
                self.generate_expression(child_node)

        self.program_lines.append(f"\tcall\t_printf")

        for child_node in print_node.children:  
            self.program_lines.append(f"\tpopl %eax")

    def generate_read(self, read_node):

        for child_node in read_node.children[::-1]:
            if child_node == read_node.children[0]:
                self.program_lines.append(f"\tpushl\t${child_node.address}")
            else:
                id_node = child_node
                n_dims = id_node.num_of_dims()
                if n_dims != 0:
                    for n_dim in range(n_dims):
                        n_index_node = id_node.children[n_dim]
                        self.generate_expression(n_index_node)

                    offset = 1
                    self.program_lines.append(f"\tmovl\t$0,\t%edx")
                    for dim in id_node.dims[::-1]:
                        self.program_lines.append(f"\tpopl\t%eax")
                        self.program_lines.append(f"\timul\t${offset},\t%eax")
                        self.program_lines.append(f"\taddl\t%eax,\t%edx")
                        offset = offset * dim

                    self.program_lines.append(f"\tleal\t-{id_node.address}(%ebp, %edx, 4),\t%eax")
                else:
                    self.program_lines.append(f"\tleal\t-{id_node.address}(%ebp),\t%eax")
                self.program_lines.append(f"\tpushl\t%eax")

        self.program_lines.append(f"\tcall\t_scanf")

        for child_node in read_node.children:  
            self.program_lines.append(f"\tpopl %eax")


    def build_overhead(self):
        overhead = f"""\t.file	"{self.filename}"
	.text
	.def	___main;	.scl	2;	.type	32;	.endef
	.section .rdata,"dr"
{self.all_strings}
	.text
	.globl	_main
	.def	_main;	.scl	2;	.type	32;	.endef
_main:
LFB11:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	call	___main"""
        self.program_lines.append(overhead)

    def build_tail(self):
        tail = """\tnop
	leave
	.cfi_restore 5
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
LFE11:
	.ident	"GCC: (MinGW.org GCC-8.2.0-3) 8.2.0"
	.def	_scanf;	.scl	2;	.type	32;	.endef
	.def	_printf;	.scl	2;	.type	32;	.endef"""
        self.program_lines.append(tail)

if __name__ == "__main__":
    filename = "sample_text.txt"
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    code_generator = CodeGenerator(filename=filename)
    code_generator.run()