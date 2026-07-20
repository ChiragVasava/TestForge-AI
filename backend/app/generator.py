import os
from typing import Dict, Any

def clean_module_name(filename: str) -> str:
    """Extract module name from filename (e.g., 'utils.py' -> 'utils')."""
    base = os.path.basename(filename)
    return os.path.splitext(base)[0]

def get_smart_default_value(annotation: str, field_name: str = "") -> str:
    if not annotation:
        return "None"
    ann = annotation.strip().lower()
    
    # Handle list types
    if "list" in ann or "iterable" in ann or "[" in ann:
        return "[]"
    # Handle dict types
    if "dict" in ann:
        return "{}"
        
    # Handle primitive type matches
    if "int" in ann:
        if "id" in field_name.lower():
            return "101"
        if "stock" in field_name.lower():
            return "10"
        if "quantity" in field_name.lower() or "qty" in field_name.lower():
            return "2"
        return "1"
    elif "float" in ann or "double" in ann:
        if "price" in field_name.lower() or "cost" in field_name.lower() or "amount" in field_name.lower() or "rate" in field_name.lower():
            return "50000.0"
        return "1.0"
    elif "str" in ann or "string" in ann:
        if "name" in field_name.lower():
            return '"Laptop"'
        if "email" in field_name.lower():
            return '"john@example.com"'
        if "card" in field_name.lower():
            return '"1234567812345678"'
        if "expiry" in field_name.lower() or "exp" in field_name.lower():
            return '"12/30"'
        if "cvv" in field_name.lower():
            return '"123"'
        return '"sample_string"'
    elif "bool" in ann:
        return "True"
        
    return "None"

def generate_test_template(filename: str, parsed_structure: Dict[str, Any]) -> str:
    """Generate PyTest file content based on parsed Python module structure."""
    module_name = clean_module_name(filename)
    lines = []
    
    # Imports
    lines.append("import pytest")
    
    # Gather items to import from the module
    items_to_import = []
    for c in parsed_structure.get("classes", []):
        items_to_import.append(c["name"])
    for f in parsed_structure.get("functions", []):
        items_to_import.append(f["name"])
        
    if items_to_import:
        import_stmt = f"from {module_name} import {', '.join(items_to_import)}"
        lines.append(import_stmt)
    
    lines.append("")
    
    # Generate tests for global functions
    for func in parsed_structure.get("functions", []):
        func_name = func["name"]
        is_async = func.get("is_async", False)
        args = func.get("args", [])
        return_type = func.get("return_type")
        
        lines.append(f"# Test for function {func_name}")
        if is_async:
            lines.append("@pytest.mark.asyncio")
            lines.append(f"async def test_{func_name}():")
        else:
            lines.append(f"def test_{func_name}():")
            
        lines.append("    \"\"\"Auto-generated test template for global function.\"\"\"")
        
        # Build argument mock variables
        if args:
            lines.append("    # Arrange inputs")
            for arg in args:
                arg_name = arg["name"]
                if arg_name.startswith("*"):
                    continue
                ann_str = f": {arg['annotation']}" if arg.get("annotation") else ""
                default_str = f" = {arg['default_value']}" if arg.get("has_default") else f" = {get_smart_default_value(arg.get('annotation'), arg_name)}"
                lines.append(f"    {arg_name}{ann_str}{default_str}")
        
        # Build execution call
        args_call = []
        for arg in args:
            arg_name = arg["name"]
            if arg_name.startswith("**"):
                args_call.append(f"{arg_name}")
            elif arg_name.startswith("*"):
                args_call.append(f"{arg_name}")
            else:
                args_call.append(f"{arg_name}={arg_name}")
        
        call_str = f"{func_name}({', '.join(args_call)})"
        
        lines.append("    # Act")
        if is_async:
            lines.append(f"    result = await {call_str}")
        else:
            lines.append(f"    result = {call_str}")
            
        # Build assertion
        lines.append("    # Assert")
        ret_type_clean = return_type.lower() if return_type else ""
        if "bool" in ret_type_clean:
            lines.append("    assert result in [True, False]")
        else:
            lines.append("    assert result is not None  # Replace with actual expected values")
            
        lines.append("")
        lines.append("")

    # Generate tests for classes
    for cls in parsed_structure.get("classes", []):
        class_name = cls["name"]
        methods = cls.get("methods", [])
        fields = cls.get("fields", [])
        
        lines.append(f"class Test{class_name}:")
        
        # Find __init__ method for builder fixture
        init_method = None
        for m in methods:
            if m["name"] == "__init__":
                init_method = m
                break
                
        # Generate Class Fixture
        lines.append("    @pytest.fixture")
        lines.append(f"    def {class_name.lower()}_instance(self):")
        lines.append(f"        \"\"\"Fixture to initialize {class_name} for each test.\"\"\"")
        
        init_args_str = []
        if init_method:
            init_args = init_method.get("args", [])
            # Exclude self argument
            init_args = [a for a in init_args if a["name"] != "self"]
            if init_args:
                lines.append("        # Constructor arguments info:")
                for arg in init_args:
                    arg_name = arg["name"]
                    ann = f" ({arg['annotation']})" if arg['annotation'] else ""
                    default = f" (default: {arg['default_value']})" if arg['has_default'] else ""
                    lines.append(f"        # - {arg_name}{ann}{default}")
                    
                    # Add default mocked value for constructor
                    val = arg['default_value'] if arg['has_default'] else get_smart_default_value(arg.get('annotation'), arg_name)
                    init_args_str.append(f"{arg_name}={val}")
        else:
            # Check fields if no explicit init method is defined (e.g. dataclasses)
            if fields:
                lines.append("        # Constructor fields (dataclass info):")
                for f in fields:
                    field_name = f["name"]
                    ann = f" ({f['annotation']})" if f['annotation'] else ""
                    default = f" (default: {f['default_value']})" if f['has_default'] else ""
                    lines.append(f"        # - {field_name}{ann}{default}")
                    
                    val = f['default_value'] if f['has_default'] else get_smart_default_value(f.get('annotation'), field_name)
                    init_args_str.append(f"{field_name}={val}")
                    
        lines.append(f"        return {class_name}({', '.join(init_args_str)})")
        lines.append("")
        
        # Generate tests for each method
        for m in methods:
            m_name = m["name"]
            if m_name.startswith("_") and m_name != "__init__":
                # Skip private methods, and constructor test is handled by fixture instantiation
                continue
            if m_name == "__init__":
                continue
                
            is_async = m.get("is_async", False)
            args = m.get("args", [])
            # Exclude self
            args = [a for a in args if a["name"] != "self"]
            return_type = m.get("return_type")
            
            fixture_name = f"{class_name.lower()}_instance"
            
            lines.append(f"    # Test for method {m_name}")
            if is_async:
                lines.append("    @pytest.mark.asyncio")
                lines.append(f"    async def test_{m_name}(self, {fixture_name}):")
            else:
                lines.append(f"    def test_{m_name}(self, {fixture_name}):")
                
            lines.append(f"        \"\"\"Auto-generated test template for {class_name}.{m_name}.\"\"\"")
            
            if args:
                lines.append("        # Arrange inputs")
                for arg in args:
                    arg_name = arg["name"]
                    if arg_name.startswith("*"):
                        continue
                    ann_str = f": {arg['annotation']}" if arg.get("annotation") else ""
                    default_str = f" = {arg['default_value']}" if arg.get("has_default") else " = None"
                    lines.append(f"        {arg_name}{ann_str}{default_str}")
                    
            args_call = []
            for arg in args:
                arg_name = arg["name"]
                if arg_name.startswith("**"):
                    args_call.append(f"{arg_name}")
                elif arg_name.startswith("*"):
                    args_call.append(f"{arg_name}")
                else:
                    args_call.append(f"{arg_name}={arg_name}")
            
            call_str = f"{fixture_name}.{m_name}({', '.join(args_call)})"
            
            lines.append("        # Act")
            if is_async:
                lines.append(f"        result = await {call_str}")
            else:
                lines.append(f"        result = {call_str}")
                
            lines.append("        # Assert")
            ret_type_clean = return_type.lower() if return_type else ""
            if "bool" in ret_type_clean:
                lines.append("        assert result in [True, False]")
            else:
                lines.append("        assert result is not None")
                
            lines.append("")
            
    return "\n".join(lines)
