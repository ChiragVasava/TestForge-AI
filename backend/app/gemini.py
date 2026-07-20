import os
import re
import ast
import json
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore", FutureWarning)
    import google.generativeai as genai
from typing import Dict, Any, Optional

from dotenv import load_dotenv

def get_gemini_key() -> str:
    """Retrieve Gemini API Key from environment, forcing a reload of the .env file."""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(backend_dir, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
    return os.getenv("GEMINI_API_KEY", "")

def _extract_imports_from_source(source_code: str) -> list[str]:
    """Parse source file and extract all top-level import statements."""
    try:
        tree = ast.parse(source_code)
        imports = []
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(ast.unparse(node))
        return imports
    except Exception:
        return []

def _clean_generated_code(code: str, source_imports: list[str], module_name: str) -> str:
    """
    Post-process Gemini's generated test code to fix common LLM mistakes:
    1. Remove any class/dataclass redefinitions that duplicate source code.
    2. Ensure all source imports are present at the top.
    3. Strip incomplete or duplicate import lines.
    """
    lines = code.split("\n")
    cleaned_lines = []
    skip_block = False
    indent_level = 0

    # Build a set of class names defined in the source for redefinition detection
    source_class_names = set()
    for imp in source_imports:
        # e.g. "from models import Product, OrderItem" -> {"Product", "OrderItem"}
        if "import" in imp:
            parts = imp.split("import")[-1]
            for name in parts.split(","):
                source_class_names.add(name.strip())

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Detect start of a class redefinition block
        if skip_block:
            # Exit the block when we see a non-indented non-empty line
            current_indent = len(line) - len(line.lstrip())
            if stripped and current_indent <= indent_level and not stripped.startswith("@"):
                skip_block = False
            else:
                i += 1
                continue

        # Check if this line is redefining a class from source
        class_match = re.match(r'^class\s+(\w+)', stripped)
        if class_match:
            class_name = class_match.group(1)
            if class_name in source_class_names:
                # Skip this entire class block
                skip_block = True
                indent_level = len(line) - len(line.lstrip())
                i += 1
                continue

        cleaned_lines.append(line)
        i += 1

    cleaned_code = "\n".join(cleaned_lines)

    # Inject missing source imports at the top if not already present
    existing_header = "\n".join(cleaned_lines[:10])
    injected = []
    for imp in source_imports:
        if imp not in existing_header:
            injected.append(imp)

    if injected:
        cleaned_code = "\n".join(injected) + "\n" + cleaned_code

    return cleaned_code.strip()


def suggest_edge_cases(
    code: str,
    name: str,
    element_type: str = "function",
    full_file_content: Optional[str] = None
) -> Dict[str, Any]:
    """
    Call Gemini API to generate structured test recommendations for a class or function.
    Uses the full file content as context to prevent class redefinitions and missing imports.
    Returns a dictionary containing suggestions with titles, explanations, and code.
    """
    api_key = get_gemini_key()
    if not api_key:
        return {
            "error": "Gemini API key is not configured in the backend .env. Please configure GEMINI_API_KEY in backend/.env to enable AI suggestions."
        }

    # Extract imports from the full source file for post-processing
    source_imports = _extract_imports_from_source(full_file_content or code)

    # Build the context block for the prompt
    context_block = ""
    if full_file_content and full_file_content != code:
        context_block = f"""
FULL SOURCE FILE CONTEXT (for your reference — use this to understand all imports and class definitions):
```python
{full_file_content}
```

TARGET element to analyze (the specific {element_type} named `{name}`):
```python
{code}
```
"""
    else:
        context_block = f"""
Source Code:
```python
{code}
```
"""

    try:
        genai.configure(api_key=api_key)

        prompt = f"""
You are an expert Principal QA and test automation engineer reviewing Python source code.
Analyze the following Python source code and generate 3 to 5 critical edge cases for the {element_type} named `{name}`.

Follow these strict rules WITHOUT EXCEPTION:

RULE 1 — NEVER REDEFINE CLASSES:
The test file already imports all classes from the source module. NEVER copy or redefine class bodies (e.g., `class Product:`) inside the test code. Use the imported classes directly.

RULE 2 — NEVER ADD MISSING IMPORTS:
Do not add `from dataclasses import dataclass`, `import sys`, `from typing import List`, or any imports that are not already used in a standard pytest file. Only use `import pytest` and `from <module> import <Names>`.

RULE 3 — MEANINGFUL ASSERTIONS ONLY:
Every test must assert actual computed values, state changes, or exception types. Forbidden: `assert True`, `assert result is not None`, `assert x == x`.

RULE 4 — VALID CONSTRUCTOR CALLS ONLY:
Never call constructors with empty arguments if fields are required. Infer realistic values: `Product(id=101, name="Laptop", price=50000.0, stock=10)`.

RULE 5 — USE PARAMETRIZE FOR SIMILAR INPUTS:
When multiple tests call the same method with different inputs, collapse them into a single `@pytest.mark.parametrize` test.

RULE 6 — EXCEPTION TESTING:
Use `with pytest.raises(ExceptionType):` to test error paths. Do not write a test that expects an exception without using `pytest.raises`.

RULE 7 — DESCRIPTIVE NAMES:
Use clear snake_case test function names like `test_get_cost_with_negative_price` instead of `test_1`.

RULE 8 — TEST BEHAVIOR, NOT PYTHON DEFAULTS:
Do not write tests that only verify Python stored a value (e.g., `assert stock == -10`). Test what your application does with that input — whether it validates, calculates, or raises an error.

{context_block}

Your entire response MUST be a valid JSON object matching the following structure:
{{
    "suggestions": [
        {{
            "title": "Title of the edge case",
            "explanation": "Explanation of what is tested and why.",
            "test_code": "import pytest\\nfrom models import Product\\n\\ndef test_example():\\n    # valid test code\\n    assert result == expected_value"
        }}
    ]
}}

CRITICAL: Return only the raw JSON. Do not wrap the output in markdown code blocks like ```json ... ``` or standard ```. Do not add any text before or after the JSON.
"""

        # Use Pro model for better instruction-following
        model = genai.GenerativeModel("gemini-2.5-pro")

        response = model.generate_content(prompt)
        text = response.text.strip()

        # Safety clean if model returns markdown wrapping
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        # Parse JSON
        parsed_data = json.loads(text)

        # Post-process each suggestion's test_code to strip class redefinitions
        if "suggestions" in parsed_data:
            for suggestion in parsed_data["suggestions"]:
                if "test_code" in suggestion and suggestion["test_code"]:
                    suggestion["test_code"] = _clean_generated_code(
                        suggestion["test_code"],
                        source_imports,
                        name
                    )

        return parsed_data

    except json.JSONDecodeError as je:
        return {
            "error": "Failed to parse AI response as JSON",
            "raw_response": text if 'text' in locals() else str(je)
        }
    except Exception as e:
        return {
            "error": f"Error calling Gemini API: {str(e)}"
        }

