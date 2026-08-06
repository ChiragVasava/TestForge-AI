# Walkthrough - TestForge AI CI/CD & Scanner CLI Integration

We have successfully integrated a custom GitHub Actions CI/CD pipeline with the TestForge AI test intelligence engine. This integration is designed around a standalone, platform-independent CLI scanner (`scripts/testforge_scanner.py`) that executes locally as well as in the cloud.

---

## Technical Architecture

The architecture separates the **CI/CD orchestration layer** from the **core intelligence engine**:

```mermaid
graph TD
    Developer[Developer commits code] -->|Create Pull Request| GHA[GitHub Actions Runner]
    GHA -->|Checkout code| Checkout[Git Checkout & Setup]
    Checkout -->|Run Test Suite| PyTest[Run PyTest & Generate coverage.json]
    PyTest -->|Call Scanner CLI| Scanner[python scripts/testforge_scanner.py --publish]
    
    subgraph testforge_scanner.py (Intelligence Engine)
        Scanner -->|Git Diff Engine| Diff[Identify Added/Modified Lines]
        Scanner -->|AST Parser| Complexity[Calculate Cyclomatic Complexity]
        Scanner -->|Git Log Engine| History[Compute Modification Frequency]
        Scanner -->|Coverage Mapper| Map[Calculate Changed Code Coverage & Gaps]
        Scanner -->|Risk Analyzer| Risk[Calculate Risk Level & Change Impact Score]
        Scanner -->|Gemini AI Engine| Gemini[Query Gemini 2.5 Flash for Edge Cases]
    end
    
    Gemini -->|Compile Report| Markdown[Generate testforge_report.md]
    Markdown -->|PR Comment API| Post[GitHub PR Comments Endpoint]
    Post -->|Add/Update Comment| PR[GitHub Pull Request Discussion Page]
```

---

## Key Features Implemented

### 1. Standalone, Platform-Independent CLI ([testforge_scanner.py](file:///c:/Users/Chirag%20Vasava/Downloads/College/Final%20Projects/TestForge/scripts/testforge_scanner.py))
- Designed to run **locally** (by developers in pre-commit hooks or local testing) and in **any CI runner** (GitHub Actions, GitLab CI, Azure Pipelines, Jenkins).
- Auto-detects local environments and falls back gracefully to `git status` check if target comparison branches or GITHUB variables are not set.

### 2. Deep Metrics & Risk Scoring Engine (Phase 2)
- **Changed Code Line Coverage**: Maps test coverage down to the exact lines added or modified, rather than just file-level averages.
- **AST Cyclomatic Complexity**: Parses code into an Abstract Syntax Tree to calculate decision density (branches, loops, try-catch, boolean conditions).
- **Modification Frequency**: Reads git log history (`git log --follow`) to assess stability risk based on commit frequency.
- **Risk Score Algorithm**:
  $$\text{Risk Score} = (0.4 \times \text{Coverage Gap}) + (0.3 \times \text{Complexity}) + (0.2 \times \text{Lines Changed}) + (0.1 \times \text{Modification Frequency})$$
  Classified into `LOW` (< 30), `MEDIUM` (30 - 69), and `HIGH` ($\ge$ 70) risk levels.

### 3. Bundled Gemini 2.5 Flash API Suggestions (Phase 3)
- Automatically extracts the function bodies of all modified functions lacking 80% coverage.
- Sends a single, optimized bundled prompt to Gemini 2.5 Flash to retrieve unit test edge cases and assertions (reducing network latency and API usage).

### 4. Smart PR Commenting Engine (Phase 4)
- Leverages Python's standard `urllib` library to post reports back to the GitHub PR.
- Includes **anti-spam deduplication**: queries past PR comments and updates the previous TestForge comment in place rather than repeatedly posting new comments.

---

## CI/CD Pipeline Configuration ([testforge_ci.yml](file:///c:/Users/Chirag%20Vasava/Downloads/College/Final%20Projects/TestForge/.github/workflows/testforge_ci.yml))
- Triggered on all pushes and pull requests to `main`.
- Grants `pull-requests: write` permissions scope to allow comment writing.
- Sequentially checks out code, runs tests with `pytest-cov`, runs the scanner CLI, and uploads outputs as build artifacts.

---

## Local Verification Output

A local execution on the staged branch successfully targeted the edited files and generated the following Quality Intelligence Report:

- **Overall Project Coverage**: 0.0%
- **Change Impact Score**: 90.5/100 (🔴 HIGH IMPACT)
- **Coverage Gap Status**: FAILED
- **File Breakdown**:
  - `scripts/testforge_scanner.py`: 528 lines, Complexity 95, Coverage 0.0%, Risk Score 90.5 (🔴 HIGH)
- **AI-Suggested Edge Cases**: Successfully generated mock PyTest scripts for the missing coverage blocks in `get_git_changed_lines()`, `calculate_cyclomatic_complexity()`, and others.
