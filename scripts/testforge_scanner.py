#!/usr/bin/env python3
import os
import sys
import argparse
import json
import subprocess
import ast
from typing import List, Dict, Any, Set, Tuple

def get_git_changed_lines(target_branch: str) -> Dict[str, Set[int]]:
    """Runs git diff to identify modified lines in new and modified Python files."""
    changed_files_lines = {}
    
    # Try different diff targets to support both CI/CD and local environments
    commands = [
        ["git", "diff", "-U0", target_branch],
        ["git", "diff", "-U0", "HEAD"],  # Compare against last commit
        ["git", "diff", "-U0"]          # Compare unstaged changes
    ]
    
    diff_output = ""
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if result.stdout.strip():
                diff_output = result.stdout
                break
        except Exception:
            continue
            
    if not diff_output:
        # Fallback: if no diff output, use git status to at least find untracked/modified Python files
        try:
            status_result = subprocess.run(
                ["git", "status", "--short"],
                capture_output=True,
                text=True,
                check=True
            )
            for line in status_result.stdout.strip().split("\n"):
                if not line:
                    continue
                status, filepath = line[:2].strip(), line[2:].strip()
                if filepath.endswith(".py"):
                    # For untracked/new files, we'll mark line 1 as changed so they're registered
                    changed_files_lines[filepath] = {1}
        except Exception as ex:
            print(f"Warning: Git fallback failed: {str(ex)}")
        return changed_files_lines

    current_file = None
    for line in diff_output.splitlines():
        if line.startswith("+++ b/"):
            # Extract file path, removing any prefix if applicable
            current_file = line[6:]
            if current_file.endswith(".py"):
                changed_files_lines[current_file] = set()
            else:
                current_file = None
        elif line.startswith("@@ ") and current_file:
            # Parse hunk header: @@ -old_range +new_range @@
            # e.g. @@ -10,2 +10,4 @@ or @@ -5 +5 @@
            parts = line.split(" ")
            if len(parts) >= 3:
                new_range = parts[2]
                if new_range.startswith("+"):
                    range_parts = new_range[1:].split(",")
                    start = int(range_parts[0])
                    length = int(range_parts[1]) if len(range_parts) > 1 else 1
                    for i in range(start, start + length):
                        changed_files_lines[current_file].add(i)
                        
    return changed_files_lines

def calculate_cyclomatic_complexity(filepath: str) -> int:
    """Calculates a basic Cyclomatic Complexity metric using AST node counts."""
    if not os.path.exists(filepath):
        return 1
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code)
        complexity = 1
        for node in ast.walk(tree):
            # Nodes representing decision branches
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity
    except Exception as e:
        print(f"Warning: Failed to calculate complexity for {filepath}: {e}")
        return 1

def get_modification_frequency(filepath: str) -> int:
    """Queries git commit history to find how many times a file has been modified."""
    try:
        result = subprocess.run(
            ["git", "log", "--follow", "--oneline", "--", filepath],
            capture_output=True,
            text=True,
            check=True
        )
        commits = result.stdout.strip().splitlines()
        return len(commits) if commits else 1
    except Exception:
        return 1

def get_function_line_ranges(filepath: str) -> List[Dict[str, Any]]:
    """Extracts function names and their start/end line numbers from a Python file AST."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code)
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = node.lineno
                # Node end_lineno is standard in Python 3.8+
                end = getattr(node, "end_lineno", start)
                functions.append({
                    "name": node.name,
                    "start": start,
                    "end": end
                })
        return functions
    except Exception as e:
        print(f"Warning: Failed to parse function ranges for {filepath}: {e}")
        return []

def extract_function_source(filepath: str, start_line: int, end_line: int) -> str:
    """Extracts the source code lines of a specific function from a file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # start_line is 1-indexed, so we slice from start_line-1 to end_line
        return "".join(lines[start_line - 1 : end_line])
    except Exception as e:
        print(f"Warning: Failed to extract function code from {filepath} [{start_line}-{end_line}]: {e}")
        return ""

def load_env_file():
    """Loads dotenv configurations from the workspace directory."""
    try:
        from dotenv import load_dotenv
        # Check current dir
        if os.path.exists(".env"):
            load_dotenv(".env")
        # Check backend/.env
        elif os.path.exists("backend/.env"):
            load_dotenv("backend/.env")
    except ImportError:
        pass

def parse_coverage_report(coverage_path: str) -> Dict[str, Any]:
    """Reads coverage.json file and extracts file-level coverage information."""
    if not os.path.exists(coverage_path):
        print(f"Warning: Coverage file not found at {coverage_path}")
        return {"totals": {"percent_covered": 0.0}, "files": {}}
        
    try:
        with open(coverage_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"Error reading coverage report: {str(e)}")
        return {"totals": {"percent_covered": 0.0}, "files": {}}

def find_coverage_entry(filepath: str, coverage_files: Dict[str, Any]) -> Tuple[str, Dict[str, Any]] | None:
    """Finds matching coverage file entry by normalizing paths and comparing suffixes."""
    norm_file = filepath.replace("\\", "/").strip("/")
    for cov_key, cov_val in coverage_files.items():
        norm_cov = cov_key.replace("\\", "/").strip("/")
        if norm_file == norm_cov or norm_file.endswith("/" + norm_cov) or norm_cov.endswith("/" + norm_file):
            return cov_key, cov_val
    return None

def analyze_risk(
    changed_lines_count: int,
    complexity: int,
    mod_frequency: int,
    coverage_gap: float
) -> Tuple[float, str]:
    """Calculates normalized Risk Score (0-100) and Level (LOW, MEDIUM, HIGH)."""
    # Normalize factors to 0-100 scale
    norm_complexity = min(100.0, complexity * 3.0)       # complexity 33+ is max risk
    norm_lines_changed = min(100.0, changed_lines_count * 2.0)  # 50 lines changed is max risk
    norm_frequency = min(100.0, mod_frequency * 5.0)     # 20+ commits is max frequency risk
    
    # Formula: 40% Coverage Gap + 30% Complexity + 20% Lines Changed + 10% Modification Frequency
    risk_score = (0.4 * coverage_gap) + (0.3 * norm_complexity) + (0.2 * norm_lines_changed) + (0.1 * norm_frequency)
    risk_score = round(min(100.0, risk_score), 2)
    
    if risk_score >= 70.0:
        level = "HIGH"
    elif risk_score >= 30.0:
        level = "MEDIUM"
    else:
        level = "LOW"
        
    return risk_score, level

def generate_gemini_suggestions(function_gaps: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Queries Gemini API in a single bundled request to generate edge cases for low-coverage functions."""
    load_env_file()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found. Skipping Gemini test suggestions.")
        return {}
        
    # Gather function info to send
    functions_info = []
    for entry in function_gaps:
        filepath = entry["file"]
        for func_name, missing_lines in entry["gaps"].items():
            if func_name == "global/module level":
                continue
                
            # Find line ranges
            func_ranges = get_function_line_ranges(filepath)
            start_line, end_line = None, None
            for fn in func_ranges:
                if fn["name"] == func_name:
                    start_line = fn["start"]
                    end_line = fn["end"]
                    break
                    
            if start_line is not None and end_line is not None:
                source_code = extract_function_source(filepath, start_line, end_line)
                if source_code:
                    functions_info.append({
                        "file": filepath,
                        "name": func_name,
                        "missing_lines": missing_lines,
                        "source_code": source_code
                    })
                    
    if not functions_info:
        return {}
        
    # Limit to top 5 functions to keep payload clean and optimize api calls
    functions_info = functions_info[:5]
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        prompt = """You are an expert QA and test automation engineer.
We have identified the following functions with missing test coverage in our project.
Analyze their source code and generate 2 to 3 critical edge cases, extreme inputs, or exception triggers to cover the missing lines.

"""
        for idx, fn in enumerate(functions_info):
            prompt += f"--- Function #{idx+1}: `{fn['name']}` in file `{fn['file']}` ---\n"
            prompt += f"Missing Line Numbers: {fn['missing_lines']}\n"
            prompt += f"Source Code:\n```python\n{fn['source_code']}\n```\n\n"
            
        prompt += """Return your response as a valid JSON object matching this structure:
{
    "suggestions": {
        "filename::function_name": [
            {
                "title": "Title of the edge case",
                "explanation": "Explanation of how to cover the missing lines.",
                "test_code": "def test_example():\\n    # pytest code here"
            }
        ]
    }
}

Ensure the keys in the "suggestions" dictionary match the exact format "filename::function_name" (e.g. "scripts/testforge_scanner.py::get_git_changed_lines").
CRITICAL: Return only the raw JSON. Do not wrap the output in markdown code blocks like ```json ... ``` or standard ```. Do not add any text before or after the JSON.
"""
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean markdown code blocks from model response
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        data = json.loads(text)
        return data.get("suggestions", {})
    except Exception as e:
        print(f"Warning: Failed to query Gemini API for suggestions: {e}")
        return {}

def get_github_pr_number() -> int | None:
    """Detects and parses the pull request number from GitHub environment variables."""
    # Method 1: parse GITHUB_EVENT_PATH
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if event_path and os.path.exists(event_path):
        try:
            with open(event_path, "r", encoding="utf-8") as f:
                event_data = json.load(f)
            pr_num = event_data.get("pull_request", {}).get("number")
            if pr_num:
                return int(pr_num)
        except Exception as e:
            print(f"Warning: Failed to parse GitHub event JSON: {e}")
            
    # Method 2: parse GITHUB_REF (e.g. refs/pull/123/merge)
    ref = os.getenv("GITHUB_REF", "")
    if "refs/pull/" in ref:
        parts = ref.split("/")
        if len(parts) >= 3:
            try:
                return int(parts[2])
            except ValueError:
                pass
                
    return None

def publish_github_comment(repo: str, pr_number: int, token: str, markdown_content: str):
    """Publishes the markdown report as a comment to the GitHub PR. Updates previous comment to avoid duplicate spam."""
    import urllib.request
    import urllib.parse
    
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "TestForge-AI-Scanner",
        "Content-Type": "application/json"
    }
    
    # Identify if a previous TestForge report exists to update it
    existing_comment_id = None
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            comments = json.loads(response.read().decode("utf-8"))
            for c in comments:
                if "# 🥈 TestForge AI - Quality Intelligence Report" in c.get("body", ""):
                    existing_comment_id = c.get("id")
                    break
    except Exception as e:
        print(f"Warning: Could not query existing PR comments: {e}. Defaulting to posting a new comment.")
        
    payload = {"body": markdown_content}
    data = json.dumps(payload).encode("utf-8")
    
    try:
        if existing_comment_id:
            # Update existing comment: PATCH /repos/{repo}/issues/comments/{comment_id}
            comment_url = f"https://api.github.com/repos/{repo}/issues/comments/{existing_comment_id}"
            req = urllib.request.Request(comment_url, data=data, headers=headers, method="PATCH")
            print(f"Updating existing PR comment (ID: {existing_comment_id})...")
        else:
            # Create new comment: POST /repos/{repo}/issues/{pr_number}/comments
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            print("Creating new PR comment...")
            
        with urllib.request.urlopen(req) as response:
            print("Successfully published quality report to GitHub PR.")
    except Exception as e:
        print(f"Error publishing comment to GitHub: {e}")

def generate_report(
    changed_files: Dict[str, Set[int]],
    coverage_data: Dict[str, Any],
    output_path: str = None
) -> Tuple[str, Dict[str, Any]]:
    """Generates the advanced SaaS-style quality intelligence report with Risk analysis."""
    overall_coverage = coverage_data.get("totals", {}).get("percent_covered", 0.0)
    overall_coverage = round(overall_coverage, 2)
    
    files_breakdown = []
    function_gaps_details = []
    
    total_risk_score = 0.0
    impactful_files_count = 0
    
    for filepath, changed_lines in changed_files.items():
        if not filepath.endswith(".py"):
            continue
            
        complexity = calculate_cyclomatic_complexity(filepath)
        mod_frequency = get_modification_frequency(filepath)
        
        # Check coverage
        cov_match = find_coverage_entry(filepath, coverage_data.get("files", {}))
        
        changed_code_coverage = 100.0
        cov_gap = 0.0
        executable_changed_count = 0
        covered_changed_count = 0
        missing_changed_lines = []
        
        if cov_match:
            _, cov_entry = cov_match
            executed_lines = set(cov_entry.get("executed_lines", []))
            missing_lines = set(cov_entry.get("missing_lines", []))
            executable_lines = executed_lines.union(missing_lines)
            
            executable_changed = changed_lines.intersection(executable_lines)
            executable_changed_count = len(executable_changed)
            
            if executable_changed_count > 0:
                covered_changed = executable_changed.intersection(executed_lines)
                covered_changed_count = len(covered_changed)
                changed_code_coverage = (covered_changed_count / executable_changed_count) * 100.0
                missing_changed_lines = sorted(list(executable_changed.intersection(missing_lines)))
                cov_gap = 100.0 - changed_code_coverage
            else:
                # No executable lines were changed (e.g. only comments or docstrings changed)
                changed_code_coverage = 100.0
                cov_gap = 0.0
        else:
            # File is missing coverage data entirely (untested file)
            changed_code_coverage = 0.0
            cov_gap = 100.0
            # Treat all changed lines as missing coverage
            missing_changed_lines = sorted(list(changed_lines))
            
        risk_score, risk_level = analyze_risk(len(changed_lines), complexity, mod_frequency, cov_gap)
        total_risk_score += risk_score
        impactful_files_count += 1
        
        files_breakdown.append({
            "file": filepath,
            "lines_changed": len(changed_lines),
            "complexity": complexity,
            "coverage": round(changed_code_coverage, 2),
            "risk_score": risk_score,
            "risk_level": risk_level
        })
        
        # Function coverage gaps analysis
        if missing_changed_lines:
            func_ranges = get_function_line_ranges(filepath)
            gaps_by_func = {}
            
            for line in missing_changed_lines:
                func_name = "global/module level"
                for fn in func_ranges:
                    if fn["start"] <= line <= fn["end"]:
                        func_name = fn["name"]
                        break
                if func_name not in gaps_by_func:
                    gaps_by_func[func_name] = []
                gaps_by_func[func_name].append(line)
                
            function_gaps_details.append({
                "file": filepath,
                "gaps": gaps_by_func
            })
            
    # Calculate overall Change Impact Score
    change_impact_score = round(total_risk_score / impactful_files_count, 2) if impactful_files_count > 0 else 0.0
    
    impact_level = "LOW"
    if change_impact_score >= 70.0:
        impact_level = "HIGH"
    elif change_impact_score >= 30.0:
        impact_level = "MEDIUM"
        
    overall_status = "🟢 Passed" if overall_coverage >= 80.0 else "🟡 Warning"
    
    # Generate Gemini suggestions for gaps
    gemini_suggestions = {}
    if function_gaps_details:
        print("Calling Gemini API to suggest edge cases for coverage gaps...")
        gemini_suggestions = generate_gemini_suggestions(function_gaps_details)
    
    # Generate SaaS quality report
    markdown = []
    markdown.append("# 🥈 TestForge AI - Quality Intelligence Report\n")
    
    # Summary Table
    markdown.append("### 📊 Quality Intelligence Metrics")
    markdown.append("| Metric | Value | Status |")
    markdown.append("| :--- | :--- | :--- |")
    markdown.append(f"| **Overall Project Coverage** | {overall_coverage}% | {overall_status} |")
    
    impact_emoji = "🔴" if impact_level == "HIGH" else "🟡" if impact_level == "MEDIUM" else "🟢"
    markdown.append(f"| **Change Impact Score** | {change_impact_score}/100 | {impact_emoji} {impact_level} IMPACT |")
    
    gap_status = "FAILED" if any(f["coverage"] < 80.0 for f in files_breakdown) else "PASSED"
    gap_emoji = "⚠️ Action Required" if gap_status == "FAILED" else "🟢 Ready"
    markdown.append(f"| **Coverage Gap Status** | {gap_status} | {gap_emoji} |")
    markdown.append("")
    
    # Changed Files Breakdown Table
    markdown.append("### 📂 Changed Files & Coverage Breakdown")
    markdown.append("| File | Lines Changed | Complexity | Changed Code Coverage | Risk Score | Risk Level |")
    markdown.append("| :--- | :---: | :---: | :---: | :---: | :--- |")
    for f in files_breakdown:
        risk_color = "🔴" if f["risk_level"] == "HIGH" else "🟡" if f["risk_level"] == "MEDIUM" else "🟢"
        markdown.append(f"| `{f['file']}` | {f['lines_changed']} | {f['complexity']} | {f['coverage']}% | {f['risk_score']} | {risk_color} {f['risk_level']} |")
    markdown.append("")
    
    # Detailed Coverage Gaps
    if function_gaps_details:
        markdown.append("### 🔍 Coverage Gaps & Functions details")
        for detail in function_gaps_details:
            markdown.append(f"#### 📄 `{detail['file']}`")
            for func_name, lines in detail["gaps"].items():
                lines_str = ", ".join(map(str, lines))
                markdown.append(f"- **Function `{func_name}()`**: missing test coverage on line(s): `{lines_str}`")
        markdown.append("")
        
    # AI Suggestions
    if gemini_suggestions:
        markdown.append("### 🤖 AI-Suggested Edge Cases (Gemini)")
        
        # Group suggestions by file
        suggestions_by_file = {}
        for key, suggs in gemini_suggestions.items():
            if "::" in key:
                file_part, func_part = key.split("::", 1)
            else:
                file_part, func_part = "General", key
                
            if file_part not in suggestions_by_file:
                suggestions_by_file[file_part] = {}
            suggestions_by_file[file_part][func_part] = suggs
            
        for file_part, funcs in suggestions_by_file.items():
            markdown.append(f"#### 📄 `{file_part}`")
            for func_part, suggs in funcs.items():
                markdown.append(f"##### Function `{func_part}()`")
                for s in suggs:
                    markdown.append(f"- **{s.get('title', 'Edge Case')}**:")
                    markdown.append(f"  {s.get('explanation', '')}")
                    test_code = s.get('test_code', '')
                    if test_code:
                        markdown.append("  ```python")
                        # indent test code to look clean inside bullet points
                        indented_code = "\n".join("  " + l for l in test_code.splitlines())
                        markdown.append(indented_code)
                        markdown.append("  ```")
            markdown.append("")
            
    # Recommendations
    markdown.append("### 💡 Recommendation")
    if gap_status == "FAILED":
        markdown.append("🔴 **Merge Blocked**: Test coverage of changed code does not meet the 80% threshold. Please add test cases covering the missing lines identified above before merging.")
    else:
        markdown.append("🟢 **Ready for Merge**: All changed files meet quality standards and cover at least 80% of modified execution paths.")
        
    markdown_str = "\n".join(markdown)
    
    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_str)
        print(f"Report saved to {output_path}")
        
    report_data = {
        "overall_coverage": overall_coverage,
        "change_impact_score": change_impact_score,
        "impact_level": impact_level,
        "gap_status": gap_status,
        "files_breakdown": files_breakdown,
        "function_gaps": function_gaps_details,
        "gemini_suggestions": gemini_suggestions
    }
    
    return markdown_str, report_data

def main():
    parser = argparse.ArgumentParser(description="TestForge AI Standalone Scanner CLI")
    parser.add_argument("--coverage", default="coverage.json", help="Path to coverage.json file")
    parser.add_argument("--diff", default="origin/main", help="Target branch for git diff comparison")
    parser.add_argument("--output", help="Optional path to output the markdown report")
    parser.add_argument("--publish", action="store_true", help="Post comment to GitHub PR")
    
    args = parser.parse_args()
    
    print("--- Running TestForge AI Standalone Scanner CLI ---")
    print(f"Diff target: {args.diff}")
    print(f"Coverage file: {args.coverage}")
    
    # 1. Get changed files and line numbers
    changes = get_git_changed_lines(args.diff)
    print(f"Changes detected in {len(changes)} Python files.")
    
    # 2. Parse coverage report
    cov = parse_coverage_report(args.coverage)
    
    # 3. Generate report
    report_md, report_data = generate_report(changes, cov, args.output)
    
    print("\n--- Console Summary ---")
    print(f"Overall Coverage: {report_data['overall_coverage']}%")
    print(f"Change Impact Score: {report_data['change_impact_score']}/100 ({report_data['impact_level']} IMPACT)")
    print(f"Coverage Gap Status: {report_data['gap_status']}")
    print("-----------------------")
    
    # 4. Publish report to GitHub PR if requested
    if args.publish:
        token = os.getenv("GITHUB_TOKEN")
        repo = os.getenv("GITHUB_REPOSITORY")
        pr_number = get_github_pr_number()
        
        if not token or not repo or not pr_number:
            print("Warning: GITHUB_TOKEN, GITHUB_REPOSITORY, or PR number is missing. Skipping PR comment publish.")
            print(f"Details - Token present: {bool(token)}, Repo: {repo}, PR: {pr_number}")
        else:
            publish_github_comment(repo, pr_number, token, report_md)
            
if __name__ == "__main__":
    main()
