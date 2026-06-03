import os
import sys
import shutil
import uuid
import subprocess
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

def get_backend_dir() -> str:
    """Get absolute path to backend directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_venv_python() -> str:
    """Locate virtual environment Python executable."""
    backend_dir = get_backend_dir()
    # On Windows, python is in Scripts/python.exe
    venv_python = os.path.join(backend_dir, ".venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        return venv_python
    # Fallback to current system python
    return sys.executable

def parse_junit_xml(xml_path: str) -> Dict[str, Any]:
    """Parse JUnit XML report to extract test status, timing, and errors."""
    if not os.path.exists(xml_path):
        return {"error": "JUnit XML report not generated. Syntax error or compilation failure in code.", "summary": {"total": 0, "passed": 0, "failed": 0, "skipped": 0}, "cases": []}
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        return {"error": f"Failed to parse JUnit XML: {str(e)}", "summary": {"total": 0, "passed": 0, "failed": 0, "skipped": 0}, "cases": []}

    suites = [root] if root.tag == "testsuite" else root.findall("testsuite")
    
    test_cases = []
    total_passed = 0
    total_failed = 0
    total_errors = 0
    total_skipped = 0
    
    for suite in suites:
        failures = int(suite.attrib.get("failures", 0))
        errors = int(suite.attrib.get("errors", 0))
        skipped = int(suite.attrib.get("skipped", 0))
        tests = int(suite.attrib.get("tests", 0))
        
        total_failed += failures
        total_errors += errors
        total_skipped += skipped
        total_passed += (tests - failures - errors - skipped)
        
        for case in suite.findall("testcase"):
            name = case.attrib.get("name")
            classname = case.attrib.get("classname")
            time = float(case.attrib.get("time", 0.0))
            
            status = "passed"
            failure_message = None
            
            # Check for failure element
            fail_el = case.find("failure")
            if fail_el is not None:
                status = "failed"
                failure_message = fail_el.text or fail_el.attrib.get("message", "Test failed")
                
            err_el = case.find("error")
            if err_el is not None:
                status = "error"
                failure_message = err_el.text or err_el.attrib.get("message", "Execution error")
                
            skip_el = case.find("skipped")
            if skip_el is not None:
                status = "skipped"
                failure_message = skip_el.attrib.get("message", "Test skipped")
                
            test_cases.append({
                "name": name,
                "classname": classname,
                "time": time,
                "status": status,
                "failure_message": failure_message
            })
            
    return {
        "summary": {
            "total": total_passed + total_failed + total_errors + total_skipped,
            "passed": total_passed,
            "failed": total_failed + total_errors,
            "skipped": total_skipped
        },
        "cases": test_cases
    }

def parse_coverage_json(json_path: str) -> Dict[str, Any]:
    """Parse pytest-cov JSON output."""
    if not os.path.exists(json_path):
        return {"percentage": 0.0, "files": {}, "error": "Coverage JSON report not generated"}
        
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        percent = data.get("totals", {}).get("percent_covered", 0.0)
        # Round it to 2 decimal places
        percent = round(percent, 2)
        
        # Extract files info
        files_data = {}
        for filepath, fileinfo in data.get("files", {}).items():
            # Only report coverage of non-test files to be clean
            if not os.path.basename(filepath).startswith("test_"):
                files_data[os.path.basename(filepath)] = {
                    "percent_covered": round(fileinfo.get("summary", {}).get("percent_covered", 0.0), 2),
                    "missing_lines": fileinfo.get("missing_lines", []),
                    "executed_lines": fileinfo.get("executed_lines", []),
                    "num_statements": fileinfo.get("summary", {}).get("num_statements", 0)
                }
                
        return {
            "percentage": percent,
            "files": files_data
        }
    except Exception as e:
        return {"percentage": 0.0, "files": {}, "error": f"Failed to parse coverage JSON: {str(e)}"}

def execute_tests(project_files: List[Dict[str, str]], test_files: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Write project files and test files to a temporary sandbox,
    execute pytest with coverage, parse results, and cleanup.
    """
    backend_dir = get_backend_dir()
    temp_root = os.path.join(backend_dir, "temp_runs")
    os.makedirs(temp_root, exist_ok=True)
    
    run_id = uuid.uuid4().hex
    run_dir = os.path.join(temp_root, run_id)
    os.makedirs(run_dir, exist_ok=True)
    
    try:
        # Write project source files
        for pf in project_files:
            file_path = os.path.join(run_dir, pf["filename"])
            # Support folders inside the zip (create nested dirs if filename has slashes)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(pf["content"])
                
        # Write test files
        for tf in test_files:
            file_path = os.path.join(run_dir, tf["filename"])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(tf["content"])
                
        # Run pytest command
        python_bin = get_venv_python()
        
        # We run pytest targeting only our run_dir
        cmd = [
            python_bin, 
            "-m", "pytest", 
            "--junitxml=report.xml", 
            "--cov=.", 
            "--cov-report=json",
            "-v"
        ]
        
        # Run subprocess
        result = subprocess.run(
            cmd, 
            cwd=run_dir, 
            capture_output=True, 
            text=True, 
            timeout=30  # Safety timeout
        )
        
        stdout_logs = result.stdout + "\n" + result.stderr
        
        # Paths to output files
        xml_path = os.path.join(run_dir, "report.xml")
        cov_path = os.path.join(run_dir, "coverage.json")
        
        # Parse output files
        test_results = parse_junit_xml(xml_path)
        coverage_results = parse_coverage_json(cov_path)
        
        # If there's an execution error (e.g. pytest crashed or exited with code 4 - no tests collected)
        # we adjust status
        status = "passed"
        if test_results.get("summary", {}).get("failed", 0) > 0:
            status = "failed"
        elif test_results.get("error"):
            status = "failed"
        
        return {
            "status": status,
            "passed_count": test_results.get("summary", {}).get("passed", 0),
            "failed_count": test_results.get("summary", {}).get("failed", 0),
            "coverage_percentage": coverage_results.get("percentage", 0.0),
            "stdout_logs": stdout_logs,
            "coverage_report": json.dumps(coverage_results),
            "test_cases": test_results.get("cases", [])
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "passed_count": 0,
            "failed_count": 0,
            "coverage_percentage": 0.0,
            "stdout_logs": f"Execution error: {str(e)}",
            "coverage_report": json.dumps({"percentage": 0.0, "files": {}, "error": str(e)}),
            "test_cases": []
        }
        
    finally:
        # Cleanup temporary run directory
        if os.path.exists(run_dir):
            shutil.rmtree(run_dir, ignore_errors=True)
