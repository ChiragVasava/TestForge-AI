import ast
from typing import Dict, Any

def parse_function_node(node: ast.FunctionDef | ast.AsyncFunctionDef) -> Dict[str, Any]:
    """Extract metadata from a function or method AST node."""
    # Arguments
    args = []
    
    # Calculate offset for arguments with default values
    defaults_offset = len(node.args.args) - len(node.args.defaults)
    
    for idx, arg in enumerate(node.args.args):
        arg_meta = {
            "name": arg.arg,
            "annotation": ast.unparse(arg.annotation) if arg.annotation else None,
            "has_default": idx >= defaults_offset
        }
        if arg_meta["has_default"]:
            default_val = node.args.defaults[idx - defaults_offset]
            arg_meta["default_value"] = ast.unparse(default_val)
        args.append(arg_meta)

    # Keyword-only arguments
    kw_defaults_offset = len(node.args.kwonlyargs) - len(node.args.kw_defaults)
    for idx, arg in enumerate(node.args.kwonlyargs):
        arg_meta = {
            "name": arg.arg,
            "annotation": ast.unparse(arg.annotation) if arg.annotation else None,
            "has_default": False
        }
        # kw_defaults can contain None for arguments with no default
        default_val = node.args.kw_defaults[idx] if idx < len(node.args.kw_defaults) else None
        if default_val:
            arg_meta["has_default"] = True
            arg_meta["default_value"] = ast.unparse(default_val)
        args.append(arg_meta)

    # *args and **kwargs
    if node.args.vararg:
        args.append({
            "name": f"*{node.args.vararg.arg}",
            "annotation": ast.unparse(node.args.vararg.annotation) if node.args.vararg.annotation else None,
            "has_default": False
        })
    if node.args.kwarg:
        args.append({
            "name": f"**{node.args.kwarg.arg}",
            "annotation": ast.unparse(node.args.kwarg.annotation) if node.args.kwarg.annotation else None,
            "has_default": False
        })

    return {
        "name": node.name,
        "is_async": isinstance(node, ast.AsyncFunctionDef),
        "args": args,
        "return_type": ast.unparse(node.returns) if node.returns else None,
        "docstring": ast.get_docstring(node),
        "lineno": node.lineno,
        "end_lineno": node.end_lineno
    }

def scan_code(source_code: str) -> Dict[str, Any]:
    """Parse python source code and extract functions, classes, and imports."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return {
            "error": f"Syntax error at line {e.lineno}, col {e.offset}: {e.text}",
            "classes": [],
            "functions": [],
            "imports": []
        }

    classes = []
    functions = []
    imports = []

    for node in tree.body:
        # Imports
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(ast.unparse(node))
            
        # Top-level Functions
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(parse_function_node(node))
            
        # Classes
        elif isinstance(node, ast.ClassDef):
            class_methods = []
            class_fields = []
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    class_methods.append(parse_function_node(child))
                elif isinstance(child, ast.AnnAssign):
                    if isinstance(child.target, ast.Name):
                        class_fields.append({
                            "name": child.target.id,
                            "annotation": ast.unparse(child.annotation) if child.annotation else None,
                            "has_default": child.value is not None,
                            "default_value": ast.unparse(child.value) if child.value is not None else None
                        })
                elif isinstance(child, ast.Assign):
                    for target in child.targets:
                        if isinstance(target, ast.Name):
                            class_fields.append({
                                "name": target.id,
                                "annotation": None,
                                "has_default": True,
                                "default_value": ast.unparse(child.value) if child.value is not None else None
                            })
                    
            classes.append({
                "name": node.name,
                "docstring": ast.get_docstring(node),
                "methods": class_methods,
                "fields": class_fields,
                "lineno": node.lineno,
                "end_lineno": node.end_lineno
            })

    return {
        "classes": classes,
        "functions": functions,
        "imports": imports
    }
