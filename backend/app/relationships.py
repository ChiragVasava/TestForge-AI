import ast
from typing import List, Dict, Any, Set
from app.generator import clean_module_name

def analyze_project_relationships(project_files: List[Any]) -> Dict[str, Any]:
    """
    Analyzes all files in a project to extract:
    1. File-to-File relationships (imports, composition, usage)
    2. Class-to-Class relationships (inheritance, composition, injection)
    3. Hierarchical tree levels (topological ordering from Root Orchestrators to Leaf Models)
    """
    # 1. Parse all files and gather registry
    file_map: Dict[str, Dict[str, Any]] = {}
    class_to_file: Dict[str, str] = {}
    all_classes_meta: Dict[str, Dict[str, Any]] = {}

    for pf in project_files:
        filename = pf.filename
        module_name = clean_module_name(filename)
        content = pf.content or ""

        parsed_classes = []
        parsed_functions = []
        raw_imports = []
        imported_modules = set()
        imported_names = {} # imported_name -> source_module

        try:
            tree = ast.parse(content)
            for node in tree.body:
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        raw_imports.append(alias.name)
                        imported_modules.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ""
                    raw_imports.append(mod)
                    imported_modules.add(mod)
                    for alias in node.names:
                        imported_names[alias.name] = mod

                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    parsed_functions.append({
                        "name": node.name,
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                        "args": [a.arg for a in node.args.args if a.arg != "self"]
                    })

                elif isinstance(node, ast.ClassDef):
                    bases = [ast.unparse(b) for b in node.bases]
                    methods = []
                    for child in node.body:
                        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            m_args = []
                            for a in child.args.args:
                                m_args.append({
                                    "name": a.arg,
                                    "annotation": ast.unparse(a.annotation) if a.annotation else None
                                })
                            methods.append({
                                "name": child.name,
                                "args": m_args,
                                "is_async": isinstance(child, ast.AsyncFunctionDef)
                            })
                    
                    is_exc = any("Exception" in b or "Error" in b for b in bases) or node.name.endswith("Error")
                    is_enum = any("Enum" in b for b in bases)
                    
                    cls_meta = {
                        "name": node.name,
                        "file": filename,
                        "module": module_name,
                        "bases": bases,
                        "methods": methods,
                        "is_exception": is_exc,
                        "is_enum": is_enum
                    }
                    parsed_classes.append(cls_meta)
                    class_to_file[node.name] = filename
                    all_classes_meta[node.name] = cls_meta
        except Exception:
            pass

        file_map[filename] = {
            "filename": filename,
            "module_name": module_name,
            "classes": parsed_classes,
            "functions": parsed_functions,
            "raw_imports": raw_imports,
            "imported_modules": imported_modules,
            "imported_names": imported_names
        }

    # 2. Build Graph Nodes & Edges
    file_nodes = []
    class_nodes = []
    file_edges = []
    class_edges = []
    
    # Track dependencies for tree level calculation:
    # file_deps[A] = set of files that A depends on (A -> B means A imports/depends on B)
    file_deps: Dict[str, Set[str]] = {fn: set() for fn in file_map}
    file_dependents: Dict[str, Set[str]] = {fn: set() for fn in file_map} # who depends on fn

    # 2a. Determine File-to-File Connections
    for filename, fdata in file_map.items():
        module = fdata["module_name"]

        # Check explicit imports matching other project files
        for other_fn, other_data in file_map.items():
            if other_fn == filename:
                continue
            other_mod = other_data["module_name"]

            is_imported = (
                other_mod in fdata["imported_modules"] or
                other_fn in fdata["raw_imports"] or
                any(other_mod == src_mod for src_mod in fdata["imported_names"].values())
            )

            # Check if any class in this file uses a class defined in other file
            has_class_dep = False
            for cls in fdata["classes"]:
                for m in cls["methods"]:
                    for a in m["args"]:
                        if a["name"] == "self":
                            continue
                        ann = a.get("annotation") or ""
                        arg_norm = a["name"].lower().replace("_", "")
                        for other_cls in other_data["classes"]:
                            oc_name = other_cls["name"]
                            if oc_name in ann or oc_name.lower().replace("_", "") == arg_norm:
                                has_class_dep = True
                                break

            if is_imported or has_class_dep:
                file_deps[filename].add(other_fn)
                file_dependents[other_fn].add(filename)
                
                rel_type = "imports" if is_imported else "composes"
                file_edges.append({
                    "id": f"edge_file_{filename}_{other_fn}",
                    "source": f"file:{filename}",
                    "target": f"file:{other_fn}",
                    "label": rel_type,
                    "type": "smoothstep",
                    "animated": True,
                    "style": {
                        "stroke": "#6366f1" if rel_type == "imports" else "#10b981",
                        "strokeWidth": 2
                    }
                })

    # 2b. Determine Class-to-Class Connections (Inheritance & Composition)
    for cls_name, cls in all_classes_meta.items():
        # Check inheritance
        for base in cls["bases"]:
            if base in all_classes_meta and base != cls_name:
                class_edges.append({
                    "id": f"edge_class_inherit_{cls_name}_{base}",
                    "source": f"class:{cls_name}",
                    "target": f"class:{base}",
                    "label": "inherits",
                    "type": "smoothstep",
                    "style": {"stroke": "#a855f7", "strokeWidth": 2}
                })

        # Check composition / dependency injection in methods
        for m in cls["methods"]:
            for a in m["args"]:
                if a["name"] == "self":
                    continue
                ann = a.get("annotation") or ""
                arg_norm = a["name"].lower().replace("_", "")
                for other_cls_name in all_classes_meta:
                    if other_cls_name == cls_name:
                        continue
                    if other_cls_name in ann or other_cls_name.lower().replace("_", "") == arg_norm:
                        edge_id = f"edge_class_comp_{cls_name}_{other_cls_name}"
                        if not any(e["id"] == edge_id for e in class_edges):
                            class_edges.append({
                                "id": edge_id,
                                "source": f"class:{cls_name}",
                                "target": f"class:{other_cls_name}",
                                "label": "depends_on",
                                "type": "smoothstep",
                                "style": {"stroke": "#10b981", "strokeWidth": 2}
                            })

    # 3. Calculate Tree Order / Hierarchical Levels
    # In tree structure:
    # Level 0 = Roots / High-level orchestrators (depended on by nobody or top entrypoints)
    # Level 1 = Intermediate domain services
    # Level 2 = Leaf models / Utilities / Exceptions
    file_levels: Dict[str, int] = {}
    
    # Files with 0 incoming dependencies (no one depends on them) are top-level roots
    # E.g., `main.py`, `library_manager.py`
    roots = [fn for fn in file_map if len(file_dependents[fn]) == 0]
    if not roots and file_map:
        # If there is a cycle or all have dependents, pick the one with most outgoing deps
        roots = [max(file_map.keys(), key=lambda fn: len(file_deps[fn]))]

    # Assign levels using BFS from roots
    visited = set()
    queue = [(r, 0) for r in roots]
    while queue:
        curr, lvl = queue.pop(0)
        if curr not in visited or lvl > file_levels.get(curr, 0):
            file_levels[curr] = max(file_levels.get(curr, 0), lvl)
            visited.add(curr)
            for child in file_deps[curr]:
                queue.append((child, lvl + 1))

    # Catch any unvisited disconnected files
    for fn in file_map:
        if fn not in file_levels:
            file_levels[fn] = 0

    max_level = max(file_levels.values()) if file_levels else 0
    leafs = [fn for fn in file_map if len(file_deps[fn]) == 0]

    # 4. Construct Node Payloads
    for filename, fdata in file_map.items():
        lvl = file_levels.get(filename, 0)
        cls_count = len(fdata["classes"])
        fn_count = len(fdata["functions"])
        
        # Categorize architectural role
        if filename in roots and lvl == 0:
            role = "Orchestrator / Root"
            badge_color = "indigo"
        elif filename in leafs:
            role = "Entity / Leaf Module"
            badge_color = "emerald"
        else:
            role = "Service / Component"
            badge_color = "cyan"

        file_nodes.append({
            "id": f"file:{filename}",
            "type": "fileNode",
            "data": {
                "label": filename,
                "module": fdata["module_name"],
                "role": role,
                "badgeColor": badge_color,
                "level": lvl,
                "classes": [c["name"] for c in fdata["classes"]],
                "functions": [f["name"] for f in fdata["functions"]],
                "dependsOn": list(file_deps[filename]),
                "dependedBy": list(file_dependents[filename]),
                "classesCount": cls_count,
                "functionsCount": fn_count
            }
        })

    for cls_name, cmeta in all_classes_meta.items():
        fn = cmeta["file"]
        lvl = file_levels.get(fn, 0)
        class_nodes.append({
            "id": f"class:{cls_name}",
            "type": "classNode",
            "data": {
                "label": cls_name,
                "file": fn,
                "level": lvl,
                "isException": cmeta["is_exception"],
                "isEnum": cmeta["is_enum"],
                "bases": cmeta["bases"],
                "methodsCount": len(cmeta["methods"]),
                "methods": [m["name"] for m in cmeta["methods"]]
            }
        })

    # Group files into tree hierarchy levels
    levels_summary = {}
    for lvl_idx in range(max_level + 1):
        files_at_lvl = [fn for fn, l in file_levels.items() if l == lvl_idx]
        if files_at_lvl:
            levels_summary[f"Level {lvl_idx}"] = files_at_lvl

    return {
        "file_nodes": file_nodes,
        "file_edges": file_edges,
        "class_nodes": class_nodes,
        "class_edges": class_edges,
        "tree": {
            "max_depth": max_level,
            "levels": levels_summary,
            "roots": roots,
            "leafs": leafs
        },
        "stats": {
            "total_files": len(file_map),
            "total_classes": len(all_classes_meta),
            "total_dependencies": len(file_edges),
            "total_class_relationships": len(class_edges)
        }
    }
