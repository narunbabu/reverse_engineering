# utils/code_utils.py

import ast
import logging
from typing import Any, Dict, List, Optional

def has_meaningful_code(code: str, logger: Optional[logging.Logger] = None) -> bool:
    """
    Determine if the Python code contains meaningful executable statements.

    Args:
        code (str): The Python code to check.
        logger (Optional[logging.Logger]): Logger to log debug information.

    Returns:
        bool: True if there's executable code, False otherwise.
    """
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
                ast.Import,
                ast.ImportFrom,
                ast.Assign,
                ast.AnnAssign,
                ast.Expr,
                ast.For,
                ast.While,
                ast.If,
                ast.With,
                ast.Try,
                ast.Raise,
                ast.Return,
                ast.Delete,
                ast.Global,
                ast.Nonlocal,
                ast.Assert,
                ast.AsyncWith,
                ast.AsyncFor,
                ast.Yield,
                ast.YieldFrom,
                ast.Lambda,
                ast.AugAssign,
            )):
                return True
        return False
    except SyntaxError as e:
        if logger:
            logger.error(f"SyntaxError while parsing code: {e}")
        return False
