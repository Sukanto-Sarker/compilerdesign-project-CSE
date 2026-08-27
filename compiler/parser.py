from dataclasses import dataclass


class ParserError(Exception):
    pass


@dataclass
class NumberNode:
    value: float


@dataclass
class VariableNode:
    name: str


@dataclass
class BinaryOpNode:
    operator: str
    left: object
    right: object


@dataclass
class AssignmentNode:
    name: str
    expression: object


@dataclass
class PrintNode:
    expression: object


@dataclass
class ProgramNode:
    statements: list


class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos]

    def eat(self, token_type):
        token = self.current()

        if token.type != token_type:
            raise ParserError(
                f"Expected {token_type}, found "
                f"'{token.value or token.type}' "
                f"at line {token.line}, column {token.column}"
            )

        self.pos += 1
        return token

    def parse(self):
        self.eat("START")

        statements = []

        while self.current().type not in ("END", "EOF"):
            statements.append(self.statement())

        self.eat("END")
        self.eat("EOF")

        return ProgramNode(statements)

    def statement(self):

        if self.current().type == "IDENTIFIER":
            return self.assignment()

        if self.current().type == "PRINT":
            return self.print_statement()

        token = self.current()

        raise ParserError(
            f"Unexpected token '{token.value}' "
            f"at line {token.line}, column {token.column}"
        )

    def assignment(self):
        name = self.eat("IDENTIFIER").value

        self.eat("ASSIGN")

        expression = self.expression()

        self.eat("SEMICOLON")

        return AssignmentNode(name, expression)

    def print_statement(self):
        self.eat("PRINT")

        expression = self.expression()

        self.eat("SEMICOLON")

        return PrintNode(expression)

    def expression(self):
        node = self.term()

        while self.current().type in ("PLUS", "MINUS"):

            operator = self.current().value
            self.pos += 1

            right = self.term()

            node = BinaryOpNode(
                operator,
                node,
                right
            )

        return node

    def term(self):
        node = self.factor()

        while self.current().type in ("MULTIPLY", "DIVIDE"):

            operator = self.current().value
            self.pos += 1

            right = self.factor()

            node = BinaryOpNode(
                operator,
                node,
                right
            )

        return node

    def factor(self):

        token = self.current()

        if token.type == "NUMBER":
            self.pos += 1

            value = float(token.value)

            if value.is_integer():
                value = int(value)

            return NumberNode(value)

        if token.type == "IDENTIFIER":
            self.pos += 1

            return VariableNode(token.value)

        if token.type == "LPAREN":
            self.pos += 1

            node = self.expression()

            self.eat("RPAREN")

            return node

        raise ParserError(
            f"Expected number, identifier, or expression "
            f"at line {token.line}, column {token.column}"
        )