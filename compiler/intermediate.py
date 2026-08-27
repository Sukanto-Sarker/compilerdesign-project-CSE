from parser import (
    ProgramNode,
    AssignmentNode,
    PrintNode,
    NumberNode,
    VariableNode,
    BinaryOpNode,
)


class IntermediateCodeGenerator:

    def __init__(self):
        self.temp_count = 0
        self.code = []

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def generate(self, node):

        if isinstance(node, ProgramNode):

            for statement in node.statements:
                self.generate(statement)

            return self.code

        if isinstance(node, AssignmentNode):

            result = self.generate_expression(
                node.expression
            )

            self.code.append(
                f"{node.name} = {result}"
            )

            return self.code

        if isinstance(node, PrintNode):

            result = self.generate_expression(
                node.expression
            )

            self.code.append(
                f"PRINT {result}"
            )

            return self.code

    def generate_expression(self, node):

        if isinstance(node, NumberNode):
            return str(node.value)

        if isinstance(node, VariableNode):
            return node.name

        if isinstance(node, BinaryOpNode):

            left = self.generate_expression(
                node.left
            )

            right = self.generate_expression(
                node.right
            )

            temp = self.new_temp()

            self.code.append(
                f"{temp} = {left} {node.operator} {right}"
            )

            return temp

        return ""