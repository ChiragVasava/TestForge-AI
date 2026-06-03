import os
import json
import google.generativeai as genai
from typing import Dict, Any

from dotenv import load_dotenv

def get_gemini_key() -> str:
    """Retrieve Gemini API Key from environment, forcing a reload of the .env file."""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(backend_dir, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
    return os.getenv("GEMINI_API_KEY", "")

def suggest_edge_cases(code: str, name: str, element_type: str = "function") -> Dict[str, Any]:
    """
    Call Gemini API to generate structured test recommendations for a class or function.
    Returns a dictionary containing suggestions with titles, explanations, and code.
    """
    api_key = get_gemini_key()
    if not api_key:
        return {
            "error": "Gemini API key is not configured in the backend .env. Please configure GEMINI_API_KEY in backend/.env to enable AI suggestions."
        }
        
    try:
        genai.configure(api_key=api_key)
        
        prompt = f"""
You are an expert QA and test automation engineer.
Analyze the following Python source code and generate 3 to 5 critical edge cases for the {element_type} named `{name}`.
Think about extreme inputs, empty inputs, type mismatches, exception triggers, and boundary conditions.

For each edge case, provide:
1. A title describing the edge case.
2. A detailed explanation of why it is an edge case and how to test it.
3. The exact python test code using `pytest` to verify this case. Ensure imports and mock values are clear and valid.

Your entire response MUST be a valid JSON object matching the following structure:
{{
    "suggestions": [
        {{
            "title": "Title of the edge case",
            "explanation": "Explanation of what is tested and why.",
            "test_code": "def test_example():\\n    # pytest code here\\n    assert True"
        }}
    ]
}}

CRITICAL: Return only the raw JSON. Do not wrap the output in markdown code blocks like ```json ... ``` or standard ```. Do not add any text before or after the JSON.
"""

        # Append source code to prompt
        prompt += f"\n\nSource Code:\n```python\n{code}\n```"

        # Initialize model
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Call model
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
