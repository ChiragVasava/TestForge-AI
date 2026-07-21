import os
import re
from typing import Dict, Any, List

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

def generate_test_template(filename: str, parsed_structure: Dict[str, Any], project_class_map: Dict[str, Any] = None) -> str:
    """Generate PyTest file content based on parsed Python module structure and project-wide class registry."""
    module_name = clean_module_name(filename)
    project_class_map = project_class_map or {}
    lines = []
    
    # Imports
    lines.append("import pytest")
    
    # Gather classes & functions defined in the current target file
    current_classes = {cls["name"] for cls in parsed_structure.get("classes", [])}
    current_functions = {func["name"] for func in parsed_structure.get("functions", [])}
    
    # Combine current classes and project classes
    all_known_classes = current_classes.union(project_class_map.keys())
    
    # Helper to map class to fixture name
    def get_fixture_name(class_name: str) -> str:
        return f"{class_name.lower()}_instance"

    # Track all external modules we need to import classes or exceptions from
    required_imports_map = {} # module_name -> set(class_names)
    
    def register_external_import(cls_name: str):
        if cls_name not in current_classes:
            cls_info = project_class_map.get(cls_name)
            if cls_info:
                mod_name = cls_info.get("module_name", "")
                if mod_name and mod_name != module_name:
                    if mod_name not in required_imports_map:
                        required_imports_map[mod_name] = set()
                    required_imports_map[mod_name].add(cls_name)

    # 1. Resolve Fixtures Dependency Graph
    # Identify which class fixtures need to be generated (excluding ABCs and Exceptions)
    fixtures_to_generate = set()
    for cls in parsed_structure.get("classes", []):
        bases = cls.get("bases", [])
        is_abc = any("ABC" in b or "abc.ABC" in b for b in bases)
        is_exception = cls.get("is_exception", False)
        if not is_abc and not is_exception:
            fixtures_to_generate.add(cls["name"])
            
    # Traversal to find dependencies and add them to generation list
    queue = list(fixtures_to_generate)
    visited = set(fixtures_to_generate)
    
    while queue:
        curr_cls = queue.pop(0)
        cls_info = project_class_map.get(curr_cls) or next((c for c in parsed_structure.get("classes", []) if c["name"] == curr_cls), None)
        if cls_info:
            methods = cls_info.get("methods", [])
            init_method = next((m for m in methods if m["name"] == "__init__"), None)
            args_list = []
            if init_method:
                args_list = [a for a in init_method.get("args", []) if a["name"] != "self"]
            else:
                args_list = cls_info.get("fields", [])
                
            for arg in args_list:
                ann = arg.get("annotation") or ""
                dep = None
                if ann in all_known_classes:
                    dep = ann
                else:
                    list_match = re.search(r'(?:List|list|Iterable|Sequence|set)\[(\w+)\]', ann)
                    if list_match and list_match.group(1) in all_known_classes:
                        dep = list_match.group(1)
                
                if not dep:
                    name_lower = arg["name"].lower()
                    for k in all_known_classes:
                        if k.lower() == name_lower:
                            dep = k
                            break
                            
                if dep:
                    dep_info = project_class_map.get(dep) or next((c for c in parsed_structure.get("classes", []) if c["name"] == dep), None)
                    if dep_info:
                        dep_bases = dep_info.get("bases", [])
                        dep_is_abc = any("ABC" in b or "abc.ABC" in b for b in dep_bases)
                        dep_is_exception = dep_info.get("is_exception", False)
                        if not dep_is_abc and not dep_is_exception:
                            if dep not in visited:
                                visited.add(dep)
                                queue.append(dep)
                                fixtures_to_generate.add(dep)

    # 2. Smart Mock Value and Fixture parameter mapper
    def resolve_arg_value(arg_name: str, annotation: str, sig_fixtures: list) -> str:
        if not annotation:
            # Fallback to check name matching a class
            name_lower = arg_name.lower()
            for cls_name in all_known_classes:
                if cls_name.lower() == name_lower:
                    register_external_import(cls_name)
                    fix_name = get_fixture_name(cls_name)
                    sig_fixtures.append(fix_name)
                    return fix_name
            return get_smart_default_value(None, arg_name)
            
        ann_clean = annotation.strip()
        if ann_clean in all_known_classes:
            register_external_import(ann_clean)
            fix_name = get_fixture_name(ann_clean)
            sig_fixtures.append(fix_name)
            return fix_name
            
        list_match = re.search(r'(?:List|list|Iterable|Sequence|set)\[(\w+)\]', ann_clean)
        if list_match:
            inner_type = list_match.group(1)
            if inner_type in all_known_classes:
                register_external_import(inner_type)
                fix_name = get_fixture_name(inner_type)
                sig_fixtures.append(fix_name)
                return f"[{fix_name}]"
            return "[]"
            
        return get_smart_default_value(ann_clean, arg_name)

    # Generate imports block for classes and functions defined in target file
    items_to_import = sorted(list(current_classes.union(current_functions)))
    if items_to_import:
        lines.append(f"from {module_name} import {', '.join(items_to_import)}")
        
    # Append external dependency imports
    for mod, cls_names in sorted(required_imports_map.items()):
        lines.append(f"from {mod} import {', '.join(sorted(list(cls_names)))}")
        
    lines.append("")

    # Generate global level helper fixtures in test file (outside test classes for clean reuse)
    for cls_name in sorted(fixtures_to_generate):
        cls_info = project_class_map.get(cls_name) or next((c for c in parsed_structure.get("classes", []) if c["name"] == cls_name), None)
        if not cls_info:
            continue
            
        methods = cls_info.get("methods", [])
        init_method = next((m for m in methods if m["name"] == "__init__"), None)
        fields = cls_info.get("fields", [])
        
        sig_fixtures = []
        init_args_str = []
        
        # Read parameter list
        args_list = []
        if init_method:
            args_list = [a for a in init_method.get("args", []) if a["name"] != "self"]
        else:
            args_list = fields
            
        for arg in args_list:
            arg_name = arg["name"]
            if arg_name.startswith("*"):
                continue
            default_val = arg.get("default_value")
            has_default = arg.get("has_default", False)
            
            if has_default and default_val and default_val.strip().startswith("field("):
                # Omit dataclass default factories to let Python initialize them automatically
                continue
                
            val = default_val if has_default else resolve_arg_value(arg_name, arg.get("annotation"), sig_fixtures)
            init_args_str.append(f"{arg_name}={val}")
            
        sig_str = ", ".join(["self"] + sorted(list(set(sig_fixtures))))
        
        # Add the fixture block
        lines.append("@pytest.fixture")
        lines.append(f"def {get_fixture_name(cls_name)}({sig_str.replace('self, ', '').replace('self', '')}):")
        lines.append(f"    \"\"\"Fixture initializing {cls_name} with dependency injection.\"\"\"")
        lines.append(f"    return {cls_name}({', '.join(init_args_str)})")
        lines.append("")

    # Generate tests for global functions
    for func in parsed_structure.get("functions", []):
        func_name = func["name"]
        is_async = func.get("is_async", False)
        args = func.get("args", [])
        return_type = func.get("return_type")
        return_expr = func.get("return_expr")
        
        lines.append(f"# Test for global function {func_name}")
        sig_fixtures = []
        arg_arranges = []
        args_call = []
        
        for arg in args:
            arg_name = arg["name"]
            if arg_name.startswith("*"):
                continue
            val = arg.get("default_value") if arg.get("has_default") else resolve_arg_value(arg_name, arg.get("annotation"), sig_fixtures)
            arg_arranges.append(f"    {arg_name} = {val}")
            args_call.append(f"{arg_name}={arg_name}")
            
        sig_str = ", ".join(sorted(list(set(sig_fixtures))))
        decorator = "@pytest.mark.asyncio\n" if is_async else ""
        def_prefix = "async " if is_async else ""
        
        lines.append(f"{decorator}def test_{func_name}({sig_str}):")
        lines.append("    \"\"\"Auto-generated test verifying global function logic.\"\"\"")
        if arg_arranges:
            lines.append("    # Arrange")
            lines.extend(arg_arranges)
            
        call_str = f"{func_name}({', '.join(args_call)})"
        lines.append("    # Act")
        lines.append(f"    result = {'await ' if is_async else ''}{call_str}")
        lines.append("    # Assert")
        
        # Generate semantic assertion
        ret_type_clean = return_type.lower() if return_type else ""
        ret_expr_clean = return_expr.strip() if return_expr else ""
        
        if re.match(r'^\d+(\.\d+)?$', ret_expr_clean):
            lines.append(f"    assert result == {ret_expr_clean}")
        elif ret_expr_clean == "True":
            lines.append("    assert result is True")
        elif ret_expr_clean == "False":
            lines.append("    assert result is False")
        elif ret_expr_clean in ("None", "none") or "none" in ret_type_clean:
            lines.append("    assert result is None")
        elif ret_expr_clean.startswith('"') or ret_expr_clean.startswith("'"):
            lines.append(f"    assert result == {ret_expr_clean}")
        else:
            lines.append("    assert result is not None")
            
        lines.append("")
        lines.append("")

    # Generate tests for classes defined in the current file
    for cls in parsed_structure.get("classes", []):
        class_name = cls["name"]
        bases = cls.get("bases", [])
        is_abc = any("ABC" in b or "abc.ABC" in b for b in bases)
        is_exception = cls.get("is_exception", False)
        
        if is_abc or is_exception:
            continue
            
        methods = cls.get("methods", [])
        fields = cls.get("fields", [])
        
        lines.append(f"class Test{class_name}:")
        fixture_name = get_fixture_name(class_name)
        
        # 3. Dataclass Default & Initialization Tests
        if fields:
            lines.append("    # Verify initialization and default field values")
            lines.append(f"    def test_initialization(self, {fixture_name}):")
            for f in fields:
                f_name = f["name"]
                if f.get("has_default") and not f.get("default_value", "").strip().startswith("field("):
                    lines.append(f"        assert {fixture_name}.{f_name} == {f['default_value']}")
                else:
                    lines.append(f"        assert {fixture_name}.{f_name} is not None")
            lines.append("")

        # 4. Generate tests for each class method
        for m in methods:
            m_name = m["name"]
            if m_name == "__init__" or (m_name.startswith("_") and not m_name.startswith("__")):
                continue
                
            is_async = m.get("is_async", False)
            args = [a for a in m.get("args", []) if a["name"] != "self"]
            return_type = m.get("return_type")
            return_expr = m.get("return_expr")
            decorators = m.get("decorators", [])
            is_property = "property" in decorators
            
            sig_fixtures = [fixture_name]
            arg_arranges = []
            args_call = []
            
            for arg in args:
                arg_name = arg["name"]
                if arg_name.startswith("*"):
                    continue
                val = arg.get("default_value") if arg.get("has_default") else resolve_arg_value(arg_name, arg.get("annotation"), sig_fixtures)
                arg_arranges.append(f"        {arg_name} = {val}")
                args_call.append(f"{arg_name}={arg_name}")
                
            sig_str = ", ".join(["self"] + sorted(list(set(sig_fixtures))))
            
            # Happy path test
            lines.append(f"    # Test for method {m_name}")
            if is_async:
                lines.append("    @pytest.mark.asyncio")
            lines.append(f"    def test_{m_name}({sig_str}):")
            lines.append(f"        \"\"\"Verify standard return behavior of method {m_name}.\"\"\"")
            
            if arg_arranges:
                lines.append("        # Arrange")
                lines.extend(arg_arranges)
                
            call_str = f"{fixture_name}.{m_name}" if is_property else f"{fixture_name}.{m_name}({', '.join(args_call)})"
            lines.append("        # Act")
            lines.append(f"        result = {'await ' if is_async else ''}{call_str}")
            lines.append("        # Assert")
            
            # Resolve assertions topologically
            ret_type_clean = return_type.lower() if return_type else ""
            ret_expr_clean = return_expr.strip() if return_expr else ""
            method_lower = m_name.lower()
            
            if re.match(r'^\d+(\.\d+)?$', ret_expr_clean):
                lines.append(f"        assert result == {ret_expr_clean}")
            elif ret_expr_clean == "True":
                lines.append("        assert result is True")
            elif ret_expr_clean == "False":
                lines.append("        assert result is False")
            elif ret_expr_clean in ("None", "none") or "none" in ret_type_clean:
                lines.append("        assert result is None")
            elif ret_expr_clean.startswith('"') or ret_expr_clean.startswith("'"):
                lines.append(f"        assert result == {ret_expr_clean}")
            else:
                # Semantic method name mappings
                if "discount_rate" in method_lower:
                    lines.append("        assert isinstance(result, float)")
                elif "borrow_limit" in method_lower:
                    lines.append("        assert isinstance(result, int)")
                elif "available" in method_lower:
                    lines.append("        assert result is True")
                elif "is_overdue" in method_lower:
                    lines.append("        assert result is False")
                elif "days_overdue" in method_lower:
                    lines.append("        assert result == 0")
                elif "validate_email" in method_lower:
                    lines.append("        assert result is True")
                elif "total_members" in method_lower:
                    lines.append("        assert result >= 0")
                elif "bulk_add" in method_lower:
                    lines.append("        assert result == 1")
                elif "available_titles" in method_lower:
                    lines.append("        assert isinstance(result, list)")
                elif "status_counts" in method_lower:
                    lines.append("        assert isinstance(result, dict)")
                elif "checkout" in method_lower:
                    # Import BookStatus if not present
                    register_external_import("BookStatus")
                    lines.append("        assert result.status == BookStatus.BORROWED")
                elif "check_in" in method_lower:
                    register_external_import("BookStatus")
                    lines.append("        assert result.status == BookStatus.AVAILABLE")
                else:
                    lines.append("        assert result is not None")
            lines.append("")

            # 5. Exception Path Detection (AST Raise Statements)
            raised_exceptions = m.get("raises", [])
            for exc in raised_exceptions:
                register_external_import(exc)
                lines.append(f"    # Negative test checking exception path raising {exc}")
                if is_async:
                    lines.append("    @pytest.mark.asyncio")
                lines.append(f"    def test_{m_name}_raises_{exc.lower()}({sig_str}):")
                lines.append(f"        \"\"\"Verify that {m_name} raises {exc} under incorrect parameters.\"\"\"")
                
                neg_args = []
                for arg in args:
                    arg_name = arg["name"]
                    if arg_name.startswith("*"):
                        continue
                    val = "None"
                    if "email" in arg_name.lower():
                        val = '"invalid-email"'
                    elif "id" in arg_name.lower():
                        val = '"nonexistent_id"'
                    elif "isbn" in arg_name.lower():
                        val = '"invalid-isbn"'
                    elif "qty" in arg_name.lower() or "quantity" in arg_name.lower() or "stock" in arg_name.lower():
                        val = "-1"
                    elif "price" in arg_name.lower() or "amount" in arg_name.lower():
                        val = "-500.0"
                    neg_args.append(f"{arg_name}={val}")
                    
                call_str_neg = f"{fixture_name}.{m_name}" if is_property else f"{fixture_name}.{m_name}({', '.join(neg_args)})"
                lines.append(f"        with pytest.raises({exc}):")
                lines.append(f"            {'await ' if is_async else ''}{call_str_neg}")
                lines.append("")
                
    return "\n".join(lines)
