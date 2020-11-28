from syntax_analyser import SyntaxAnalyser

class CodeGenerator:

    def __init__(self, filename="./sample_text.txt") -> None:
        self.filename = filename
        self.program_lines = []
        self.base_address = 16 
        self.relative_address = self.base_address
        self.stack_base = 0
        self.setup()
    
    def setup(self):
        syntax_analyser = SyntaxAnalyser(filename=self.filename)
        self.ast = syntax_analyser.build_ast()

    def run(self):
        if self.ast.node_type() != "program":
            raise Exception(f"Root node must be a program node.")

        program_node = self.ast
        self.set_scope_variables_address(program_node)

        self.build_overhead()

        self.generate_code(program_node)

        self.build_tail()

        self.ast.print_tree()

        f = open(f"{self.filename[:-4]}.s", "w")
        f.write("\n".join(self.program_lines) + "\n")
        f.close()

    def set_scope_variables_address(self, routine_node):
        for variable_node in routine_node.variable_list:
            routine_node.set_address(variable_node.name, self.relative_address)
            if variable_node.type == "int":
                self.relative_address += 4 * variable_node.num_of_items()
        self.stack_base = -self.stack_base

    def generate_code(self, node):
        if node.node_type() == "assign":
            self.generate_assign(node)
        elif node.node_type() in ["print", "println"]:
            self.generate_print(node)
        for child_node in node.children:
            self.generate_code(child_node)

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
            self.program_lines.append(f"\tmovl\t%eax,\t{variable_node.address+self.stack_base}(%ebp, %edx, 4)")
        else:
            self.program_lines.append(f"\tpopl\t%eax")
            self.program_lines.append(f"\tmovl\t%eax,\t{variable_node.address+self.stack_base}(%ebp)")

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
                self.program_lines.append(f"\tpushl\t{expression_node.address+self.stack_base}(%ebp, %edx, 4)")
            else:
                self.program_lines.append(f"\tpushl\t{expression_node.address+self.stack_base}(%esp)")
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
                variable_node = print_node.children[0]
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
            self.program_lines.append(f"\tmovl\t{variable_node.address+self.stack_base}(%ebp, %edx, 4),\t%eax")
        else:
            self.program_lines.append(f"\tmovl\t{variable_node.address+self.stack_base}(%ebp),\t%eax")

        if str_addr != "$LC2":
            self.program_lines.append(f"\tmovl\t%eax,\t4(%esp)")
        self.program_lines.append(f"\tmovl\t{str_addr},\t(%esp)")
        self.program_lines.append(f"\tcall\t_printf")

    def build_overhead(self):
        overhead = f"""\t.file	"{self.filename}.c"
	.text
	.def	___main;	.scl	2;	.type	32;	.endef
	.section .rdata,"dr"
LC0:
	.ascii "%d \\0"
LC1:
	.ascii "%d\\12\\0"
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
	andl	$-{self.base_address}, %esp
	subl	${self.relative_address}, %esp
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