from .parser import (
    ProgramNode,
    AssignmentNode,
    PrintNode,
    NumberNode,
    VariableNode,
    BinaryOpNode,
)


class SemanticError(Exception):
    pass


class SemanticAnalyzer:

    def __init__(self):
        self.symbol_table = {}

    def analyze(self, node):
        if isinstance(node, ProgramNode):

            for statement in node.statements:
                self.analyze(statement)

            return

        if isinstance(node, AssignmentNode):

            self.check_expression(node.expression)

            self.symbol_table[node.name] = {
                "type": "number"
            }

            return

        if isinstance(node, PrintNode):

            self.check_expression(node.expression)

            return

    def check_expression(self, node):

        if isinstance(node, NumberNode):
            return

        if isinstance(node, VariableNode):

            if node.name not in self.symbol_table:
                raise SemanticError(
                    f"Variable '{node.name}' is not defined"
                )

            return

        if isinstance(node, BinaryOpNode):

            self.check_expression(node.left)
            self.check_expression(node.right)

            return