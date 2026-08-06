# TestForge AI - Complete Testing & Real-World Usage Guide

This guide describes how to test every single feature of the TestForge AI platform, providing sample test cases, sample code files, and explaining the architectural reasons and real-world corporate value for each feature.

---

## 📂 1. Core Architecture: Where Is Data Saved?

| Feature | Where is it Saved? | How It Works |
| :--- | :--- | :--- |
| **Project Files** | **Server Database (`testforge.db`)** | Uploaded Python code is saved in the `project_files` table. |
| **Generated PyTest** | **Server Database (`testforge.db`)** | Generated unit test code is saved in the `generated_tests` table. |
| **Execution Sandbox** | **Server Filesystem (`backend/temp_runs/`)** | During execution, files are temporarily written to a sandbox folder, run via PyTest, and deleted immediately after. |
| **QA Test Cases** | **Server Database (`testforge.db`)** | CSV-imported or manually added cases are saved in the `test_cases` table. |
| **Externalized Test Data** | **Server Database (`testforge.db`)** | Configuration key-values (e.g. `BASE_URL`) are saved in the `test_data` table. |
| **User Login Token** | **Client Local Storage** | A JWT token is stored in the browser's local storage to persist your login session. |

---

## 🧪 2. Complete Step-by-Step Testing Guide

Follow these steps to demonstrate and test every feature of the application:

### Step 2.1: Project Setup & User Auth
1. Open your browser and navigate to `http://localhost:3000/register`.
2. Register a new user account (e.g., `tester@company.com` / `password123`).
3. Log in with your new credentials. You will be redirected to the Dashboard.
4. Click **"Create Project"** and name it **"E-Commerce Service"**.

---

### Step 2.2: Unit Testing & AST Code Elements
1. Click on the **"E-Commerce Service"** card to open the workspace.
2. Click **"Upload Python File"** and upload the following sample code (Save this locally as `payment_gateway.py` before uploading):

```python
# payment_gateway.py

class PaymentProcessor:
    """Handles payments for customers."""
    def __init__(self, merchant_id: str, currency: str = "USD"):
        self.merchant_id = merchant_id
        self.currency = currency
        self.transactions = []

    def charge(self, amount: float, card_number: str) -> bool:
        """Charges a card. Returns True if successful, raises ValueError otherwise."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if len(card_number) != 16:
            raise ValueError("Invalid card number length")
        
        # Mock payment authorization
        self.transactions.append({"amount": amount, "status": "success"})
        return True

def apply_promo_code(price: float, promo: str) -> float:
    """Applies a promotion code to a price."""
    if promo == "SAVE10":
        return price * 0.9
    elif promo == "SAVE20":
        return price * 0.8
    return price
```

3. **Verify AST Code Elements**: Look at the left sidebar under **AST Code Elements**. You will see:
   - **Classes**: `PaymentProcessor`
   - **Functions**: `apply_promo_code`
4. **Verify Source Code Viewer**: Click on the file in the sidebar. The center panel displays the exact source code of `payment_gateway.py`.
5. **Verify AI Edge Case Suggestions**:
   - In the left sidebar, click the function `apply_promo_code`.
   - The right sidebar (**Gemini Edge Cases**) will load 3-5 AI-generated edge cases (e.g. empty promo string, negative price, decimal values).
   - Select one suggestion and click the **`+` (Add to Test Suite)** button. It will append the test code to your test template in the center panel and switch to the **Generated PyTest** tab.

---

### Step 2.3: PyTest Generation, Saving & Execution
1. Click the **"Generated PyTest"** tab in the center panel. You will see a complete, auto-generated unit test suite mapping all classes and functions of `payment_gateway.py` (with fixtures and assertions).
2. Click **"Save Test File"**. This saves the test suite as `test_payment_gateway.py` in the database.
3. Click **"Execute PyTest Suite"**.
   - The top banner will update to show: `PyTest Execution Finished: PASSED`.
   - It shows the passed/failed count and **code coverage** percentage.
   - Under **Execution History** on the right side, a new run record appears. Click **"View Report"** to see detailed logs and file-by-file coverage metrics!

---

### Step 2.4: QA Automation & Test Cases (Playwright)
1. At the top of the workspace, switch the mode toggle from **"Unit & Code Testing"** to **"QA Automation & Test Cases"**.
2. **Verify Download Template**: Click **"Download Template"**. A standard CSV file named `testforge_template.csv` will download.
3. **Verify CSV Import**:
   - Save the following content as `company_testcases.csv` on your computer:
   ```csv
   title,description,steps,expected_result,test_data
   "Checkout Process","Verify items can be purchased","1. Navigate to /cart\n2. Click Checkout\n3. Enter billing info\n4. Click Complete Purchase","Confirmation page displays purchase ID","{""cart_value"": 120}"
   "Invalid Login Alert","Verify error displays on bad login","1. Navigate to /login\n2. Enter invalid email\n3. Enter invalid password\n4. Click login","Error message 'Invalid credentials' is shown",""
   ```
   - Click **"Import CSV"** and upload `company_testcases.csv`. A popup will confirm: `Successfully imported 2 test cases`.
   - The test cases will populate in the main repository table.
4. **Verify Add Test Case**:
   - Click **"Add Test Case"** on the right.
   - Enter:
     - **Title**: `Search Product`
     - **Steps**: `1. Navigate to /search\n2. Enter 'Laptop' in search box\n3. Press Enter`
     - **Expected**: `Product list shows 'MacBook Pro' and 'Dell XPS'`
   - Click **"Create Test Case"**. It will save to the table.
5. **Verify Externalized Test Data**:
   - In the middle column (**Externalized Test Data**), add a new variable:
     - **Key**: `BASE_URL`
     - **Value**: `http://localhost:3000` (or your company staging link)
     - **Description**: Target URL for QA execution
   - Click **"Save Parameter"**.
6. **Verify Playwright Automation Script Generation**:
   - In the Test Case table, locate the **Checkout Process** test case and click the **"Automate" 🪄** button.
   - The right column will call the Gemini AI engine, parameterize the steps using the `BASE_URL` you saved in the test data, and render a complete **Playwright Python script** featuring standard `goto`, page element locators, and `expect` assertions.
   - Click **"Copy Code"** to copy the script.
7. **Verify CSV Export**: Click **"Export CSV"**. A CSV file containing all your project test cases will download.

---

## ❓ 3. Frequently Asked Questions

### Q1: Does this only test the uploaded file or the whole web application?
- **Unit Testing**: It runs unit tests against **all uploaded files** in your current project. If you upload `file_a.py`, `file_b.py`, and save respective test files, they are all executed together inside a combined sandbox run, giving you a project-wide code coverage report.
- **QA Automation (Playwright)**: It generates browser scripts that are intended to test your **running web application** (defined by your `BASE_URL`).

### Q2: How do I check all tests of a project? Whole project or file by file?
- When you click **"Execute PyTest Suite"**, it runs the **whole project test suite** in one command.
- The results show **both**:
  1. An **aggregate score** (e.g. "Run #1, Passed: 8, Failed: 0, Coverage: 92%").
  2. A **file-by-file breakdown** in the detailed run report page (showing coverage percentages and missing lines for each individual source file in the project).

---

## 🏢 4. Corporate Value & Real-World Scenarios

Here is why these features are highly valuable for tech companies:

### A. Source Code Scanning & AST Parsing
- **Real-World Scenario**: A developer modifies a 1,000-line Python class in a corporate billing service.
- **Why it is useful**: Manually writing unit tests is slow. The AST parser reads the structure of the code, extracts the exact methods and argument structures, and generates a functional PyTest template automatically. The developer only has to write assertions, cutting test creation time by 80%.

### B. AI Edge Case Recommendations (Gemini)
- **Real-World Scenario**: A junior developer writes a tax calculation function: `calculate_tax(income)`. They test positive numbers but forget boundary cases.
- **Why it is useful**: The Gemini integration scans the code and warns: *"You did not handle negative income, extremely large values, or non-numeric inputs."* It provides the exact pytest code to cover these. This prevents boundary-condition bugs from ever reaching production.

### C. CSV Import/Export & Test Case Repository
- **Real-World Scenario**: Business analysts or QA leads write hundreds of manual test scenarios in Excel.
- **Why it is useful**: QA engineers can import the CSV directly into TestForge. Non-technical stakeholders can write tests in Excel/CSV, import them to TestForge, and export them back to CSV for review, keeping business logic and code synchronized.

### D. Externalized Test Data & QA Script Generator (Playwright)
- **Real-World Scenario**: A company wants to run automation tests across three environments: Dev, Staging, and Production.
- **Why it is useful**: Hardcoding URLs, logins, and settings inside test scripts is bad practice. TestForge externalizes this data into a dedicated panel. When generating the Playwright script, Gemini automatically replaces static values with dynamic parameterizations (e.g., `os.getenv("BASE_URL")` or configuration lookups). The same script can now run on Dev, Staging, or Production just by changing variables!
