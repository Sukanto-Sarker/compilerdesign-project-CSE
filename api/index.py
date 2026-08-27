import sys
import os

from flask import Flask, request, jsonify


# ============================================================
# Add project root to Python path
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# Import Compiler Modules
# ============================================================

from compiler.lexer import Lexer, LexerError
from compiler.parser import Parser, ParserError
from compiler.semantic import SemanticAnalyzer, SemanticError
from compiler.intermediate import IntermediateCodeGenerator


# ============================================================
# Flask Application
# ============================================================

app = Flask(__name__)


# ============================================================
# Token → Dictionary
# ============================================================

def token_to_dict(token):
    return {
        "type": token.type,
        "value": token.value,
        "line": token.line,
        "column": token.column
    }


# ============================================================
# AST → Dictionary
# ============================================================

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


# ============================================================
# Compiler Pipeline
# ============================================================

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


    # ========================================================
    # 1. Lexical Analysis
    # ========================================================

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


    # ========================================================
    # 2. Syntax Analysis
    # ========================================================

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


    # ========================================================
    # 3. Semantic Analysis
    # ========================================================

    try:

        semantic = SemanticAnalyzer()

        semantic.analyze(ast)

        result["symbol_table"] = semantic.symbol_table

        result["phases"]["semantic"] = "success"


    except SemanticError as error:

        result["error"] = {
            "type": "Semantic Error",
            "message": str(error)
        }

        result["phases"]["semantic"] = "error"

        return result


    # ========================================================
    # 4. Intermediate Code Generation
    # ========================================================

    try:

        generator = IntermediateCodeGenerator()

        code = generator.generate(ast)

        result["intermediate_code"] = code

        result["phases"]["intermediate"] = "success"


    except Exception as error:

        result["error"] = {
            "type": "Intermediate Code Error",
            "message": str(error)
        }

        result["phases"]["intermediate"] = "error"

        return result


    # ========================================================
    # Compilation Successful
    # ========================================================

    result["success"] = True

    return result


# ============================================================
# API Route
# ============================================================

@app.route("/", methods=["GET", "POST", "OPTIONS"])
def compile_api():

    # --------------------------------------------------------
    # CORS / Preflight Request
    # --------------------------------------------------------

    if request.method == "OPTIONS":

        response = jsonify({
            "success": True
        })

        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"

        return response


    # --------------------------------------------------------
    # GET Request
    # --------------------------------------------------------

    if request.method == "GET":

        response = jsonify({
            "success": True,
            "message": "MiniLang Compiler API is running."
        })

        response.headers["Access-Control-Allow-Origin"] = "*"

        return response


    # --------------------------------------------------------
    # POST Request
    # --------------------------------------------------------

    try:

        data = request.get_json(silent=True) or {}

        source = data.get("source", "")


        # ----------------------------------------------------
        # Empty Source Check
        # ----------------------------------------------------

        if not isinstance(source, str) or not source.strip():

            response = jsonify({
                "success": False,
                "error": {
                    "type": "Input Error",
                    "message": "Source code is empty."
                }
            })

            response.status_code = 400

            response.headers["Access-Control-Allow-Origin"] = "*"

            return response


        # ----------------------------------------------------
        # Compile Source Code
        # ----------------------------------------------------

        result = compile_source(source)


        response = jsonify(result)

        response.headers["Access-Control-Allow-Origin"] = "*"

        return response


    # --------------------------------------------------------
    # Unexpected Server Error
    # --------------------------------------------------------

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