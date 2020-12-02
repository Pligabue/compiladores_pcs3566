from node import IfNode
from syntax_analyser import SyntaxAnalyser

class CodeGenerator:

    def __init__(self, filename="./sample_text.txt") -> None:
        self.filename = filename
        self.program_lines = []
        self.relative_address = 0
        self.setup()
    
    def setup(self):
        syntax_analyser = SyntaxAnalyser(filename=self.filename)
        self.ast = syntax_analyser.build_ast()

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

        f = open(f"{self.filename[:-4]}.s", "w")
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
        self.program_lines.append(f"\tcmpl\t${limit_node.value},\t-{variable_node.address}(%ebp)")
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
            if expression_node.operation == "+":
                operation = "addl"
            elif expression_node.operation == "-":
                operation = "subl"
            elif expression_node.operation == "*":
                operation = "imul"
            else:
                raise Exception(f"Operator {expression_node.operation} doesn't exist.")
            self.program_lines.append(f"\t{operation}\t%edx,\t%eax")
            self.program_lines.append(f"\tpushl\t%eax")

    def generate_print(self, print_node):
        print_type = print_node.node_type()
        
        if print_type == "print":
            str_addr = "$LC0"
            variable_node = print_node.children[0]
        elif print_type == "println":
            if print_node.children:
                str_addr = "$LC1"
                variable_node = print_node.children[0]
            else:
                str_addr = "$LC2"
                self.program_lines.append(f"\tpushl\t{str_addr}")
                self.program_lines.append(f"\tcall\t_printf")
                self.program_lines.append(f"\tpopl %eax")
                return
        else:
            raise Exception(f"Unidentified print. Received {print_type}.")

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
            self.program_lines.append(f"\tmovl\t-{variable_node.address}(%ebp, %edx, 4),\t%eax")
        else:
            self.program_lines.append(f"\tmovl\t-{variable_node.address}(%ebp),\t%eax")

        self.program_lines.append(f"\tpushl\t%eax")
        self.program_lines.append(f"\tpushl\t{str_addr}")
        self.program_lines.append(f"\tcall\t_printf")
        self.program_lines.append(f"\tpopl %eax")
        self.program_lines.append(f"\tpopl %eax")

    def build_overhead(self):
        overhead = f"""\t.file	"{self.filename}.c"
	.text
	.def	___main;	.scl	2;	.type	32;	.endef
	.section .rdata,"dr"
LC0:
	.ascii "%3d \\0"
LC1:
	.ascii "%3d\\12\\0"
LC2:
	.ascii "\\12\\0"
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
	.def	_printf;	.scl	2;	.type	32;	.endef"""
        self.program_lines.append(tail)

if __name__ == "__main__":
    code_generator = CodeGenerator()
    code_generator.run()