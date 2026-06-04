# 🥈 TestForge AI - Quality Intelligence Report

### 📊 Quality Intelligence Metrics
| Metric | Value | Status |
| :--- | :--- | :--- |
| **Overall Project Coverage** | 0.0% | 🟡 Warning |
| **Change Impact Score** | 90.5/100 | 🔴 HIGH IMPACT |
| **Coverage Gap Status** | FAILED | ⚠️ Action Required |

### 📂 Changed Files & Coverage Breakdown
| File | Lines Changed | Complexity | Changed Code Coverage | Risk Score | Risk Level |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `scripts/testforge_scanner.py` | 611 | 118 | 0.0% | 90.5 | 🔴 HIGH |

### 🔍 Coverage Gaps & Functions details
#### 📄 `scripts/testforge_scanner.py`
- **Function `global/module level()`**: missing test coverage on line(s): `1, 2, 3, 4, 5, 6, 7, 8, 9, 74, 94, 108, 132, 143, 156, 170, 179, 204, 294, 320, 365, 568, 609, 610, 611`
- **Function `get_git_changed_lines()`**: missing test coverage on line(s): `10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73`
- **Function `calculate_cyclomatic_complexity()`**: missing test coverage on line(s): `75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93`
- **Function `get_modification_frequency()`**: missing test coverage on line(s): `95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107`
- **Function `get_function_line_ranges()`**: missing test coverage on line(s): `109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131`
- **Function `extract_function_source()`**: missing test coverage on line(s): `133, 134, 135, 136, 137, 138, 139, 140, 141, 142`
- **Function `load_env_file()`**: missing test coverage on line(s): `144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155`
- **Function `parse_coverage_report()`**: missing test coverage on line(s): `157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169`
- **Function `find_coverage_entry()`**: missing test coverage on line(s): `171, 172, 173, 174, 175, 176, 177, 178`
- **Function `analyze_risk()`**: missing test coverage on line(s): `180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203`
- **Function `generate_gemini_suggestions()`**: missing test coverage on line(s): `205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293`
- **Function `get_github_pr_number()`**: missing test coverage on line(s): `295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319`
- **Function `publish_github_comment()`**: missing test coverage on line(s): `321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364`
- **Function `generate_report()`**: missing test coverage on line(s): `366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567`
- **Function `main()`**: missing test coverage on line(s): `569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608`

### 🤖 AI-Suggested Edge Cases (Gemini)
#### 📄 `scripts/testforge_scanner.py`
##### Function `get_git_changed_lines()`
- **No Git repository / All git diff commands fail**:
  This scenario covers the failure of all `git diff` commands (lines 10-21) and the subsequent execution of the `if not diff_output` block (line 24). It also tests the fallback `git status` command failing and triggering its `except Exception` block (lines 35-42), ensuring robust error handling when git is unavailable or unresponsive.
  ```python
  import pytest
  import os
  from unittest.mock import patch, MagicMock
  from scripts.testforge_scanner import get_git_changed_lines
  
  def test_get_git_changed_lines_no_git_repo_all_fail():
      # Mock subprocess.run to raise an exception for all git commands
      with patch('subprocess.run', side_effect=Exception('Git command failed')) as mock_run:
          with patch('builtins.print') as mock_print:
              result = get_git_changed_lines('main')
              assert result == {}
              # Ensure git diff commands were attempted
              assert mock_run.call_count >= 3 # at least for diffs
              # Ensure the fallback warning was printed
              mock_print.assert_called_with(pytest.approx('Warning: Git fallback failed: Git command failed', abs=0.1))
  ```
- **Only untracked/new Python files (no diffs, triggering git status fallback)**:
  This test case ensures that all `git diff` commands return empty output (lines 10-22), leading to the execution of the `if not diff_output` block (line 24). It then simulates `git status --short` returning an untracked Python file, verifying that this file is correctly identified and marked with line 1 (lines 25-34).
  ```python
  import pytest
  import os
  from unittest.mock import patch, MagicMock
  from scripts.testforge_scanner import get_git_changed_lines
  
  def test_get_git_changed_lines_untracked_python_files():
      # Mock git diff commands to return no output
      mock_diff_result = MagicMock()
      mock_diff_result.stdout = ''
      mock_diff_result.strip.return_value = ''
  
      # Mock git status to return an untracked Python file
      mock_status_result = MagicMock()
      mock_status_result.stdout = '?? new_file.py\n A other_file.txt\n M modified_but_not_python.log'
      mock_status_result.strip.return_value = '?? new_file.py\n A other_file.txt\n M modified_but_not_python.log'
  
      def mock_subprocess_run_side_effect(cmd, **kwargs):
          if 'diff' in cmd:
              return mock_diff_result
          elif 'status' in cmd:
              return mock_status_result
          raise Exception(f'Unexpected command: {cmd}')
  
      with patch('subprocess.run', side_effect=mock_subprocess_run_side_effect) as mock_run:
          result = get_git_changed_lines('main')
          assert result == {'new_file.py': {1}}
          # Ensure git diff commands were attempted and then git status
          assert any('diff' in cmd for cmd in [call[0] for call in mock_run.call_args_list])
          assert any('status' in cmd for cmd in [call[0] for call in mock_run.call_args_list])
  ```
- **Complex git diff output with mixed Python/non-Python changes and hunks**:
  This critical test covers the main `diff_output` parsing logic (lines 44-72). It simulates a `git diff` output containing changes in multiple Python files (additions, modifications across different hunks), as well as changes in non-Python files, ensuring that non-Python files are correctly ignored (lines 51-52) and all specified Python line ranges are accurately extracted.
  ```python
  import pytest
  import os
  from unittest.mock import patch, MagicMock
  from scripts.testforge_scanner import get_git_changed_lines
  
  def test_get_git_changed_lines_complex_diff_output():
      # Simulate git diff output with changes in python and non-python files
      mock_diff_stdout = '''
  diff --git a/src/module1.py b/src/module1.py
  index abc1234..def5678 100644
  --- a/src/module1.py
  +++ b/src/module1.py
  @@ -10,2 +10,4 @@
   class MyClass:
       def method(self):
  +        new_line_1 = 1
  +        new_line_2 = 2
           print('hello')
   
  @@ -20 +24,3 @@
       # Some comment
  +    another_new_line = 3
       return True
   
  diff --git a/src/non_python_file.txt b/src/non_python_file.txt
  index ghh4567..ijk8901 100644
  --- a/src/non_python_file.txt
  +++ b/src/non_python_file.txt
  @@ -1,2 +1,3 @@
   Line 1
  +New text here
   Line 2
  diff --git a/src/module2.py b/src/module2.py
  index qwe345..rty678 100644
  --- a/src/module2.py
  +++ b/src/module2.py
  @@ -5 +5,2 @@
   def some_func():
  +    added_line_3 = 3
       pass
  '''
      mock_result = MagicMock()
      mock_result.stdout = mock_diff_stdout
      mock_result.strip.return_value = mock_diff_stdout.strip()
  
      # Mock subprocess.run to return the complex diff output for the first diff command
      with patch('subprocess.run', return_value=mock_result) as mock_run:
          result = get_git_changed_lines('main')
          expected_changes = {
              'src/module1.py': {10, 11, 12, 13, 24, 25, 26},
              'src/module2.py': {5, 6}
          }
          assert result == expected_changes
          # Ensure the first git diff command was called
          mock_run.assert_called_once_with(['git', 'diff', '-U0', 'main'], capture_output=True, text=True, check=True)
  ```
##### Function `calculate_cyclomatic_complexity()`
- **Non-existent filepath**:
  This test covers the initial `os.path.exists` check (lines 75-76), ensuring that the function correctly returns the default complexity of 1 when the specified file does not exist, without attempting to open or parse it.
  ```python
  import pytest
  import os
  from scripts.testforge_scanner import calculate_cyclomatic_complexity
  
  def test_calculate_cyclomatic_complexity_non_existent_file():
      non_existent_path = '/path/to/non_existent_file.py'
      assert not os.path.exists(non_existent_path)
      complexity = calculate_cyclomatic_complexity(non_existent_path)
      assert complexity == 1
  ```
- **File with invalid Python syntax**:
  This scenario covers the `except Exception as e:` block (lines 87-90). Providing a file with malformed Python code will cause `ast.parse(code)` to raise a `SyntaxError`, verifying that the function catches the exception, prints a warning, and returns the default complexity of 1.
  ```python
  import pytest
  import os
  import tempfile
  from unittest.mock import patch
  from scripts.testforge_scanner import calculate_cyclomatic_complexity
  
  def test_calculate_cyclomatic_complexity_invalid_syntax():
      invalid_code = "def func_error:\n    if True"
      with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
          tmp_file.write(invalid_code)
          tmp_file_path = tmp_file.name
      try:
          with patch('builtins.print') as mock_print:
              complexity = calculate_cyclomatic_complexity(tmp_file_path)
              assert complexity == 1
              mock_print.assert_called_with(pytest.approx(f"Warning: Failed to calculate complexity for {tmp_file_path}: SyntaxError: invalid syntax (line 1)", abs=0.1))
      finally:
          os.remove(tmp_file_path)
  ```
- **File with complex control flow and boolean operations**:
  This test case covers the core logic of iterating through the AST and correctly calculating complexity (lines 80-86). It includes various control flow structures (`if`, `for`, `while`, `try`, `except`) and boolean operators (`and`, `or`) to ensure that each type of decision branch is properly identified and contributes to the cyclomatic complexity count.
  ```python
  import pytest
  import os
  import tempfile
  from scripts.testforge_scanner import calculate_cyclomatic_complexity
  
  def test_calculate_cyclomatic_complexity_complex_code():
      complex_code = '''
  def complex_func(a, b, c):
      if a > 0 and b < 10:  # +1 for if, +1 for and
          for i in range(c):  # +1 for for
              while i % 2 == 0:  # +1 for while
                  print(i)
                  break
      elif a < 0 or b > 10: # +1 for elif, +1 for or
          try: # +1 for try
              result = a / b
          except ZeroDivisionError: # +1 for except
              result = 0
          finally: # +1 for finally (implicit in try/except context)
              pass
      with open('file.txt', 'r') as f: # +1 for with
          content = f.read()
      return content
  '''
      # Expected complexity: Base (1) + if (1) + and (1) + for (1) + while (1) + elif (1) + or (1) + try (1) + except (1) + with (1) = 10
      with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
          tmp_file.write(complex_code)
          tmp_file_path = tmp_file.name
      try:
          complexity = calculate_cyclomatic_complexity(tmp_file_path)
          assert complexity == 10
      finally:
          os.remove(tmp_file_path)
  ```
##### Function `get_modification_frequency()`
- **Non-existent filepath or git command fails**:
  This test case covers the `except Exception` block (lines 104-107). It simulates a scenario where `subprocess.run` fails (e.g., due to a non-existent file path that git cannot track, or git command not being available), ensuring the function gracefully handles the error and returns the default frequency of 1.
  ```python
  import pytest
  import os
  from unittest.mock import patch, MagicMock
  from scripts.testforge_scanner import get_modification_frequency
  
  def test_get_modification_frequency_command_fails():
      # Simulate subprocess.run raising an exception
      with patch('subprocess.run', side_effect=Exception('Git log failed')) as mock_run:
          frequency = get_modification_frequency('/path/to/non_existent_file.py')
          assert frequency == 1
          mock_run.assert_called_once() # Ensure it was attempted
  ```
- **Existing file with no commits in its history (empty git log output)**:
  This test focuses on the scenario where `git log` returns no output (lines 102-103). This can happen for brand new untracked files, or files committed and then reverted. It ensures that when `commits` list is empty, the function correctly returns the default frequency of 1, as specified by `len(commits) if commits else 1`.
  ```python
  import pytest
  import os
  from unittest.mock import patch, MagicMock
  from scripts.testforge_scanner import get_modification_frequency
  
  def test_get_modification_frequency_no_commits():
      mock_result = MagicMock()
      mock_result.stdout = '' # Simulate no commits found
      mock_result.strip.return_value = ''
  
      with patch('subprocess.run', return_value=mock_result) as mock_run:
          frequency = get_modification_frequency('new_untracked_file.py')
          assert frequency == 1
          mock_run.assert_called_once_with(
              ['git', 'log', '--follow', '--oneline', '--', 'new_untracked_file.py'],
              capture_output=True,
              text=True,
              check=True
          )
  ```
- **Existing file with multiple commits in history**:
  This test covers the standard successful execution path (lines 96-103). It simulates `git log` returning multiple commit entries, verifying that the function correctly parses the output and returns the accurate count of modifications for the specified file.
  ```python
  import pytest
  import os
  from unittest.mock import patch, MagicMock
  from scripts.testforge_scanner import get_modification_frequency
  
  def test_get_modification_frequency_multiple_commits():
      mock_log_output = '''
  abc1234 Add feature X
  def5678 Fix bug Y
  ghi9012 Refactor Z
  '''
      mock_result = MagicMock()
      mock_result.stdout = mock_log_output
      mock_result.strip.return_value = mock_log_output.strip()
  
      with patch('subprocess.run', return_value=mock_result) as mock_run:
          frequency = get_modification_frequency('src/example.py')
          assert frequency == 3
          mock_run.assert_called_once_with(
              ['git', 'log', '--follow', '--oneline', '--', 'src/example.py'],
              capture_output=True,
              text=True,
              check=True
          )
  ```
##### Function `get_function_line_ranges()`
- **Non-existent filepath**:
  This test covers the initial `os.path.exists` check (lines 109-110), ensuring that the function correctly returns an empty list when the specified file does not exist, without attempting to open or parse it.
  ```python
  import pytest
  import os
  from scripts.testforge_scanner import get_function_line_ranges
  
  def test_get_function_line_ranges_non_existent_file():
      non_existent_path = '/path/to/non_existent_file_for_funcs.py'
      assert not os.path.exists(non_existent_path)
      functions = get_function_line_ranges(non_existent_path)
      assert functions == []
  ```
- **File with invalid Python syntax**:
  This scenario covers the `except Exception as e:` block (lines 124-129). Providing a file with malformed Python code will cause `ast.parse(code)` to raise a `SyntaxError`, verifying that the function catches the exception, prints a warning, and returns an empty list.
  ```python
  import pytest
  import os
  import tempfile
  from unittest.mock import patch
  from scripts.testforge_scanner import get_function_line_ranges
  
  def test_get_function_line_ranges_invalid_syntax():
      invalid_code = "def func_error: # Missing parenthesis for arguments\n    pass"
      with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
          tmp_file.write(invalid_code)
          tmp_file_path = tmp_file.name
      try:
          with patch('builtins.print') as mock_print:
              functions = get_function_line_ranges(tmp_file_path)
              assert functions == []
              mock_print.assert_called_with(pytest.approx(f"Warning: Failed to parse function ranges for {tmp_file_path}: SyntaxError: invalid syntax (line 1)", abs=0.1))
      finally:
          os.remove(tmp_file_path)
  ```
- **File with multiple standard and async functions, including nested ones**:
  This test covers the core logic of iterating through the AST to find various types of function definitions (`ast.FunctionDef`, `ast.AsyncFunctionDef`) and correctly extracting their `start` and `end` line numbers (lines 114-123). It includes functions at different indentation levels and within classes to ensure robust parsing.
  ```python
  import pytest
  import os
  import tempfile
  from scripts.testforge_scanner import get_function_line_ranges
  
  def test_get_function_line_ranges_complex_functions():
      complex_code = '''
  import os
  
  def main_func(a, b):
      """Docstring"""
      if a > b:
          print('a is greater')
  
  class MyClass:
      def __init__(self):
          self.value = 0
  
      async def async_method(self, x):
          await some_awaitable()
          return x * 2
  
      def nested_func(self):
          def inner():
              pass
          inner()
  
  async def another_async_func():
      return 'done'
  '''
      # Expected ranges (adjust based on Python version and end_lineno behavior)
      # Assuming end_lineno is accurately captured for Python 3.8+
      expected_functions = [
          {'name': 'main_func', 'start': 4, 'end': 8},
          {'name': '__init__', 'start': 11, 'end': 12},
          {'name': 'async_method', 'start': 14, 'end': 16},
          {'name': 'nested_func', 'start': 18, 'end': 22},
          {'name': 'inner', 'start': 19, 'end': 20},
          {'name': 'another_async_func', 'start': 24, 'end': 25}
      ]
  
      with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
          tmp_file.write(complex_code)
          tmp_file_path = tmp_file.name
      try:
          functions = get_function_line_ranges(tmp_file_path)
          # Sort for consistent comparison as ast.walk order isn't strictly guaranteed for siblings
          functions.sort(key=lambda x: (x['start'], x['name']))
          expected_functions.sort(key=lambda x: (x['start'], x['name']))
  
          # Handle potential differences in end_lineno for 'inner' function
          # In older Python versions, end_lineno might not be available or might be same as start_lineno for small nodes
          # This test ensures basic functionality for start/end lines.
          # If actual end_lineno for 'inner' is 19, adjust expected: {'name': 'inner', 'start': 19, 'end': 19}
  
          assert len(functions) == len(expected_functions)
          for i, func in enumerate(functions):
              assert func['name'] == expected_functions[i]['name']
              assert func['start'] == expected_functions[i]['start']
              # Allow some flexibility for end_lineno of nested/simple functions across Python versions
              # As long as it's not wildly off and captures the block
              assert func['end'] >= expected_functions[i]['start'] # Must at least cover start
              # For exact match, assert func['end'] == expected_functions[i]['end']
              # For this test, we'll ensure it's within a reasonable bound or exactly matches where expected.
              if func['name'] == 'inner' and func['end'] == 19: # Python < 3.8 or specific AST behavior
                  pass # It's okay if end_lineno is 19 for inner
              else:
                  assert func['end'] == expected_functions[i]['end']
  
      finally:
          os.remove(tmp_file_path)
  ```
##### Function `extract_function_source()`
- **Non-existent filepath**:
  This test covers the `except Exception as e:` block (lines 138-142). It simulates opening a non-existent file, which will cause `open()` to raise a `FileNotFoundError`, verifying that the function catches the exception, prints a warning, and returns an empty string.
  ```python
  import pytest
  import os
  from unittest.mock import patch
  from scripts.testforge_scanner import extract_function_source
  
  def test_extract_function_source_non_existent_file():
      non_existent_path = '/path/to/non_existent_file_for_extract.py'
      assert not os.path.exists(non_existent_path)
      with patch('builtins.print') as mock_print:
          source = extract_function_source(non_existent_path, 1, 5)
          assert source == ''
          mock_print.assert_called_with(pytest.approx(f"Warning: Failed to extract function code from {non_existent_path} [1-5]: [Errno 2] No such file or directory: '{non_existent_path}'", abs=0.1))
  ```
- **Extreme or invalid line ranges (single line, start > end, end beyond EOF)**:
  This test explores edge cases for `start_line` and `end_line` parameters, focusing on how Python's list slicing handles them (line 137). It verifies that a single line function is extracted correctly (`start_line=end_line`), `start_line > end_line` results in an empty string, and `end_line` beyond the file's length still extracts correctly up to the end of the file.
  ```python
  import pytest
  import os
  import tempfile
  from scripts.testforge_scanner import extract_function_source
  
  def test_extract_function_source_extreme_line_ranges():
      code_content = '''
  Line 1
  Line 2
  Line 3
  Line 4
  Line 5
  '''
      with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
          tmp_file.write(code_content)
          tmp_file_path = tmp_file.name
      try:
          # Case 1: Single line extraction (start_line == end_line)
          source_single = extract_function_source(tmp_file_path, 3, 3)
          assert source_single == 'Line 3\n'
  
          # Case 2: start_line > end_line (should return empty string)
          source_invalid_range = extract_function_source(tmp_file_path, 5, 2)
          assert source_invalid_range == ''
  
          # Case 3: end_line is beyond EOF (should extract up to end of file)
          source_beyond_eof = extract_function_source(tmp_file_path, 4, 100)
          assert source_beyond_eof == 'Line 4\nLine 5\n'
  
          # Case 4: start_line is 1 and end_line is actual EOF
          source_full_file = extract_function_source(tmp_file_path, 1, 5)
          assert source_full_file == 'Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n'
  
      finally:
          os.remove(tmp_file_path)
  ```
- **Valid filepath and multi-line function range**:
  This test covers the standard successful execution path (lines 134-137). It provides a valid file path and a valid multi-line range, ensuring that the function correctly reads the file, slices the lines, and concatenates them into the expected source string.
  ```python
  import pytest
  import os
  import tempfile
  from scripts.testforge_scanner import extract_function_source
  
  def test_extract_function_source_valid_range():
      file_content = '''
  # Header
  def my_function():
      print('Hello')
      return True
  # Footer
  '''
      with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
          tmp_file.write(file_content)
          tmp_file_path = tmp_file.name
      try:
          # my_function starts at line 3, ends at line 5 (inclusive)
          start_line = 3
          end_line = 5
          expected_source = "def my_function():\n    print('Hello')\n    return True\n"
          source = extract_function_source(tmp_file_path, start_line, end_line)
          assert source == expected_source
      finally:
          os.remove(tmp_file_path)
  ```

### 💡 Recommendation
🔴 **Merge Blocked**: Test coverage of changed code does not meet the 80% threshold. Please add test cases covering the missing lines identified above before merging.