import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

from compiler.lexer import Lexer, LexerError
from compiler.parser import Parser, ParserError
from compiler.semantic import SemanticAnalyzer, SemanticError
from compiler.intermediate import IntermediateCodeGenerator


def token_to_dict(token):
    return {
        "type": token.type,
        "value": token.value,
        "line": token.line,
        "column": token.column
    }


def ast_to_dict(node):

    if node is None:
        return None

    result = {
        "type": node.__class__.__name__
    }

    if hasattr(node, "value"):
        result["value"] = node.value

    if hasattr(node, "name"):
        result["name"] = node.name

    if hasattr(node, "operator"):
        result["operator"] = node.operator

    if hasattr(node, "left"):
        result["left"] = ast_to_dict(node.left)

    if hasattr(node, "right"):
        result["right"] = ast_to_dict(node.right)

    if hasattr(node, "expression"):
        result["expression"] = ast_to_dict(node.expression)

    if hasattr(node, "statements"):
        result["statements"] = [
            ast_to_dict(statement)
            for statement in node.statements
        ]

    return result


def compile_source(source):

    result = {
        "success": False,
        "tokens": [],
        "ast": None,
        "symbol_table": {},
        "intermediate_code": [],
        "error": None,
        "phases": {
            "lexical": "pending",
            "syntax": "pending",
            "semantic": "pending",
            "intermediate": "pending"
        }
    }

    # -------------------------
    # Lexical Analysis
    # -------------------------

    try:
        lexer = Lexer(source)

        tokens = lexer.tokenize()

        result["tokens"] = [
            token_to_dict(token)
            for token in tokens
            if token.type != "EOF"
        ]

        result["phases"]["lexical"] = "success"

    except LexerError as error:

        result["error"] = {
            "type": "Lexical Error",
            "message": str(error)
        }

        result["phases"]["lexical"] = "error"

        return result

    # -------------------------
    # Syntax Analysis
    # -------------------------

    try:

        parser = Parser(tokens)

        ast = parser.parse()

        result["ast"] = ast_to_dict(ast)

        result["phases"]["syntax"] = "success"

    except ParserError as error:

        result["error"] = {
            "type": "Syntax Error",
            "message": str(error)
        }

        result["phases"]["syntax"] = "error"

        return result

    # -------------------------
    # Semantic Analysis
    # -------------------------

    try:

        semantic = SemanticAnalyzer()

        semantic.analyze(ast)

        result["symbol_table"] = (
            semantic.symbol_table
        )

        result["phases"]["semantic"] = "success"

    except SemanticError as error:

        result["error"] = {
            "type": "Semantic Error",
            "message": str(error)
        }

        result["phases"]["semantic"] = "error"

        return result

    # -------------------------
    # Intermediate Code
    # -------------------------

    generator = IntermediateCodeGenerator()

    code = generator.generate(ast)

    result["intermediate_code"] = code

    result["phases"]["intermediate"] = "success"

    result["success"] = True

    return result


def handler(request):

    if request.method == "OPTIONS":

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": ""
        }

    try:

        if request.method != "POST":

            return {
                "statusCode": 405,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": '{"error":"Method not allowed"}'
            }

        body = request.body

        if isinstance(body, bytes):
            body = body.decode("utf-8")

        import json

        data = json.loads(body)

        source = data.get("source", "")

        result = compile_source(source)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(result)
        }

    except Exception as error:

        import json

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "success": False,
                "error": {
                    "type": "Server Error",
                    "message": str(error)
                }
            })
        }