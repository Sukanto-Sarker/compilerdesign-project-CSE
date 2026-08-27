import re
from dataclasses import dataclass


@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int


class LexerError(Exception):
    pass


class Lexer:
    KEYWORDS = {
        "START": "START",
        "END": "END",
        "PRINT": "PRINT",
    }

    SIMPLE_TOKENS = {
        "+": "PLUS",
        "-": "MINUS",
        "*": "MULTIPLY",
        "/": "DIVIDE",
        "=": "ASSIGN",
        "(": "LPAREN",
        ")": "RPAREN",
        ";": "SEMICOLON",
    }

    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1

    def advance(self):
        char = self.source[self.pos]
        self.pos += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def tokenize(self):
        tokens = []

        while self.pos < len(self.source):
            char = self.source[self.pos]

            # Whitespace
            if char in " \t\r":
                self.advance()
                continue

            # New line
            if char == "\n":
                self.advance()
                continue

            # Comments
            if char == "#":
                while self.pos < len(self.source):
                    if self.advance() == "\n":
                        break
                continue

            start_line = self.line
            start_column = self.column

            # Identifier / keyword
            if char.isalpha() or char == "_":
                value = ""

                while self.pos < len(self.source):
                    current = self.source[self.pos]

                    if current.isalnum() or current == "_":
                        value += self.advance()
                    else:
                        break

                token_type = self.KEYWORDS.get(value.upper(), "IDENTIFIER")

                tokens.append(
                    Token(
                        token_type,
                        value,
                        start_line,
                        start_column
                    )
                )

                continue

            # Number
            if char.isdigit():
                value = ""
                dot_count = 0

                while self.pos < len(self.source):
                    current = self.source[self.pos]

                    if current.isdigit():
                        value += self.advance()

                    elif current == ".":
                        dot_count += 1

                        if dot_count > 1:
                            raise LexerError(
                                f"Invalid number at line {start_line}, "
                                f"column {start_column}"
                            )

                        value += self.advance()

                    else:
                        break

                tokens.append(
                    Token(
                        "NUMBER",
                        value,
                        start_line,
                        start_column
                    )
                )

                continue

            # Operators and symbols
            if char in self.SIMPLE_TOKENS:
                token_type = self.SIMPLE_TOKENS[char]

                self.advance()

                tokens.append(
                    Token(
                        token_type,
                        char,
                        start_line,
                        start_column
                    )
                )

                continue

            raise LexerError(
                f"Unknown character '{char}' "
                f"at line {start_line}, column {start_column}"
            )

        tokens.append(
            Token(
                "EOF",
                "",
                self.line,
                self.column
            )
        )

        return tokens