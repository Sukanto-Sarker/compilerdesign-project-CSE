import os
import sys

from flask import Flask, request, jsonify

# --------------------------------------------------
# Project root
# --------------------------------------------------

ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


# --------------------------------------------------
# Compiler imports
# --------------------------------------------------

from compiler.lexer import Lexer, LexerError
from compiler.parser import Parser, ParserError
from compiler.semantic import SemanticAnalyzer, SemanticError
from compiler.intermediate import IntermediateCodeGenerator


# --------------------------------------------------
# Flask application
# --------------------------------------------------

app = Flask(__name__)


# --------------------------------------------------
# AST conversion
# --------------------------------------------------

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
        result["expression"] = ast_to_dict(
            node.expression
        )

    if hasattr(node, "statements"):
        result["statements"] = [
            ast_to_dict(statement)
            for statement in node.statements
        ]

    return result


# --------------------------------------------------
# Token conversion
# --------------------------------------------------

def token_to_dict(token):

    return {
        "type": token.type,
        "value": token.value,
        "line": token.line,
        "column": token.column
    }


# --------------------------------------------------
# Compiler
# --------------------------------------------------

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


    # ==================================================
    # 1. LEXICAL ANALYSIS
    # ==================================================

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

        result["phases"]["lexical"] = "error"

        result["error"] = {
            "type": "Lexical Error",
            "message": str(error)
        }

        return result


    # ==================================================
    # 2. SYNTAX ANALYSIS
    # ==================================================

    try:

        parser = Parser(tokens)

        ast = parser.parse()

        result["ast"] = ast_to_dict(ast)

        result["phases"]["syntax"] = "success"


    except ParserError as error:

        result["phases"]["syntax"] = "error"

        result["error"] = {
            "type": "Syntax Error",
            "message": str(error)
        }

        return result


    # ==================================================
    # 3. SEMANTIC ANALYSIS
    # ==================================================

    try:

        semantic = SemanticAnalyzer()

        semantic.analyze(ast)

        result["symbol_table"] = semantic.symbol_table

        result["phases"]["semantic"] = "success"


    except SemanticError as error:

        result["phases"]["semantic"] = "error"

        result["error"] = {
            "type": "Semantic Error",
            "message": str(error)
        }

        return result


    # ==================================================
    # 4. INTERMEDIATE CODE GENERATION
    # ==================================================

    try:

        generator = IntermediateCodeGenerator()

        code = generator.generate(ast)

        result["intermediate_code"] = code

        result["phases"]["intermediate"] = "success"

    except Exception as error:

        result["phases"]["intermediate"] = "error"

        result["error"] = {
            "type": "Intermediate Code Error",
            "message": str(error)
        }

        return result


    # ==================================================
    # SUCCESS
    # ==================================================

    result["success"] = True

    return result


# --------------------------------------------------
# API route
# --------------------------------------------------

@app.route("/api", methods=["POST", "OPTIONS"])
def compile_api():

    # CORS preflight
    if request.method == "OPTIONS":

        response = jsonify({
            "success": True
        })

        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"

        return response


    try:

        data = request.get_json(silent=True)

        if not data:

            return jsonify({
                "success": False,
                "error": {
                    "type": "Request Error",
                    "message": "Invalid JSON request."
                }
            }), 400


        source = data.get("source", "")

        if not isinstance(source, str):

            return jsonify({
                "success": False,
                "error": {
                    "type": "Request Error",
                    "message": "Source code must be a string."
                }
            }), 400


        if not source.strip():

            return jsonify({
                "success": False,
                "error": {
                    "type": "Request Error",
                    "message": "Source code is empty."
                }
            }), 400


        result = compile_source(source)


        response = jsonify(result)

        response.headers["Access-Control-Allow-Origin"] = "*"

        return response


    except Exception as error:

        response = jsonify({
            "success": False,
            "error": {
                "type": "Server Error",
                "message": str(error)
            }
        })

        response.status_code = 500

        response.headers["Access-Control-Allow-Origin"] = "*"

        return response


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.route("/api", methods=["GET"])
def api_health():

    return jsonify({
        "success": True,
        "message": "MiniLang compiler API is running."
    })


# --------------------------------------------------
# Local development
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )