# PROJECT INTERVIEW CONTEXT: TESTFORGE AI

> **Document Purpose**: This document is a comprehensive, deeply technical architectural and implementation dossier of **TestForge AI**. It is specifically structured for an AI Technical Interviewer to thoroughly evaluate the engineer on their design decisions, codebase mastery, algorithms, security posture, limitations, and full-stack technical execution.
>
> **Repository Name**: `ChiragVasava/TestForge-AI` (Local workspace: `TestForge`)  
> **Source Verification Status**: Every claim, code snippet, and architecture pattern in this document has been directly verified against the repository's source files.

---

## 1. PROJECT OVERVIEW

### 1.1 Project Identity
- **Project Name**: TestForge AI (also referenced as `TestForge-Antigravity` in repository documentation)
- **Primary Goal**: An intelligent full-stack test automation and QA intelligence platform that unifies developer unit test generation, AST code analysis, AI-powered edge case recommendation, sandboxed PyTest execution, manual QA test case management, automated Playwright browser script generation, and CI/CD pull request risk gating into a single cohesive system.

### 1.2 Problem Statement & Industry Motivation
1. **Developer Friction in Unit Testing**: Writing comprehensive unit tests with edge cases, boundary values, mock dependencies, and fixtures is tedious and frequently skipped under deadline pressure, leading to poor code coverage and regressions in production.
2. **Untrusted Code Execution Hazards**: Naive test generation tools often import or execute user code at runtime to inspect methods, creating severe security vulnerabilities (remote code execution). TestForge AI solves this by using **Abstract Syntax Tree (AST)** static analysis to safely inspect code structure without executing it.
3. **LLM Hallucinations in Test Generation**: Standard LLMs often hallucinate missing imports, redefine classes that already exist in the source file, produce vacuous assertions (`assert True`), or generate invalid constructor parameters. TestForge AI implements an AST-guided prompt pipeline and post-generation code sanitization to enforce valid pytest code.
4. **Disconnection Between QA Teams & Developers**: QA teams manage manual test cases in spreadsheets (CSV) while developers manage code in Git. TestForge AI bridges this gap with a dual-mode workspace allowing manual test case import/export and one-click translation of plain-English test steps into parameterized Playwright automation scripts injected with externalized configuration variables.
5. **Ineffective CI/CD Coverage Metrics**: Traditional CI/CD tools measure naive repository-wide line coverage averages, hiding critical coverage gaps in newly modified code. TestForge AI provides a standalone CI/CD scanner (`testforge_scanner.py`) that calculates line-level coverage gaps on git diffs and computes an algorithmic **Weighted Change Impact / Risk Score**.

### 1.3 Target Users & Personas
- **Software Engineers / Backend Developers**: Upload Python files, explore interactive AST hierarchies, auto-generate boilerplate PyTest suites, generate AI edge cases, run tests in an isolated sandbox, and review statement-level coverage reports with missing line indicators.
- **QA Engineers & SDETs**: Manage manual test case repositories, bulk import/export CSV suites, define centralized environment variables (`BASE_URL`, `ADMIN_EMAIL`), and translate manual test steps into executable Playwright Python scripts.
- **Engineering Leads & DevOps**: Monitor test run histories, inspect execution logs, enforce an 80% changed-code coverage gate in GitHub Actions, and view automated PR risk intelligence comments.

### 1.4 Technology Stack (Actually Found in Code)

| Domain | Technology | Evidence / Version |
|---|---|---|
| **Frontend Framework** | Next.js | `16.2.6` (App Router, Turbopack/Webpack) in `frontend/package.json` |
| **Frontend UI Library** | React & React-DOM | `19.2.4` in `frontend/package.json` |
| **Language (Frontend)** | TypeScript | `v5` (strict mode enabled in `frontend/tsconfig.json`) |
| **Styling & Theme** | Vanilla Tailwind CSS | `@tailwindcss/postcss` & `tailwindcss` `v4` in `frontend/package.json` |
| **Icons** | Lucide React | `^1.17.0` in `frontend/package.json` |
| **Visualizations** | Recharts | `^3.8.1` in `frontend/package.json` |
| **Backend Framework** | FastAPI | `fastapi` in `backend/requirements.txt` (ASGI app in `backend/app/main.py`) |
| **ASGI Web Server** | Uvicorn | `uvicorn` in `backend/requirements.txt` |
| **Language (Backend)** | Python 3 | `python-version: '3.10'` specified in `.github/workflows/testforge_ci.yml` |
| **Static Code Parsing** | Python AST | Standard library `ast` in `backend/app/parser.py`, `generator.py`, `scripts/testforge_scanner.py` |
| **Database & ORM** | SQLite & SQLAlchemy | SQLite via `sqlalchemy` engine in `backend/app/database.py`, models in `backend/app/models.py` |
| **Validation & Schema** | Pydantic & email-validator | `pydantic`, `email-validator` in `backend/app/schemas.py` |
| **Authentication & Tokens**| Python-Jose & Hashlib PBKDF2 | `python-jose[cryptography]` (JWT `HS256`), Python `hashlib.pbkdf2_hmac` & `secrets` in `backend/app/auth.py` |
| **AI LLM Integration** | Google Generative AI | `google-generativeai` (Gemini 2.5 Flash & Pro) in `backend/app/gemini.py` |
| **Test Runner & Sandbox** | PyTest & Subprocess | `pytest`, `pytest-cov`, `pytest-asyncio` via `subprocess.run` in `backend/app/executor.py` |
| **Browser Automation** | Playwright (Python) | Code generation targets Playwright sync/async API in `backend/app/routers/testcases.py` |
| **DevOps & CI/CD** | GitHub Actions & Custom CLI | `.github/workflows/testforge_ci.yml` invoking `scripts/testforge_scanner.py` |

---

## 2. COMPLETE PROJECT STRUCTURE

```
TestForge/
├── .github/
│   └── workflows/
│       └── testforge_ci.yml          # GitHub Actions CI pipeline configuration
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── ai.py                 # POST /api/ai/recommend (Gemini edge cases)
│   │   │   ├── auth.py               # POST /api/auth/register, /login, /login/json, GET /me
│   │   │   ├── projects.py           # CRUD /api/projects, file upload, AST structure view
│   │   │   ├── testcases.py          # CRUD test cases, CSV import/export, Playwright gen, test data
│   │   │   └── tests.py              # GET /generate, POST /save, POST /run, GET /runs history
│   │   ├── auth.py                   # PBKDF2 hashing, JWT signing/decoding, OAuth2 dependencies
│   │   ├── config.py                 # Env configurations (SECRET_KEY, ALGORITHM, GEMINI_API_KEY)
│   │   ├── database.py               # SQLAlchemy engine setup (SQLite), Base, get_db session yield
│   │   ├── executor.py               # Sandboxed test runner, temp dir management, JUnit XML / coverage parser
│   │   ├── gemini.py                 # Gemini client config, prompt engineering, code post-processing
│   │   ├── generator.py              # AST metadata → PyTest test template code generator
│   │   ├── main.py                   # FastAPI initialization, CORS origins, router aggregation
│   │   ├── models.py                 # SQLAlchemy relational ORM models
│   │   ├── parser.py                 # Python AST static analyzer (extracts classes, functions, raises)
│   │   ├── schemas.py                # Pydantic input/output schemas
│   │   └── test_config.py            # Pytest unit test validating config constants
│   ├── check_db.py                   # Diagnostic script to inspect SQLite database contents
│   ├── requirements.txt              # Backend Python dependencies
│   └── testforge.db                  # Local SQLite database instance
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── login/
│   │   │   │   └── page.tsx          # Login page (email/password, JWT storage)
│   │   │   ├── register/
│   │   │   │   └── page.tsx          # Registration page (form validation, account creation)
│   │   │   ├── projects/
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx      # Dual-mode workspace (Unit Testing vs QA Automation)
│   │   │   │       └── runs/
│   │   │   │           └── [run_id]/
│   │   │   │               └── page.tsx # Test execution report, coverage breakdown, logs viewer
│   │   │   ├── globals.css           # Custom dark-mode styles, scrollbars, badge utilities
│   │   │   ├── layout.tsx            # Root layout with Geist font configurations
│   │   │   └── page.tsx              # Projects dashboard (list, create, delete, overview metrics)
│   │   └── lib/
│   │       └── api.ts                # Fetch wrapper with JWT Bearer token auto-injection & 401 redirect
│   ├── package.json                  # Next.js & React dependencies
│   ├── postcss.config.mjs            # PostCSS configuration for Tailwind v4
│   └── tsconfig.json                 # TypeScript compiler options
├── scripts/
│   └── testforge_scanner.py          # Standalone CLI quality scanner for git diffs, risk scoring & PR comments
├── MD_Files/                         # Reference docs, audits, guides, and Render configurations
├── .gitignore
├── coverage.json                     # Root-level coverage output from CI
└── README.md                         # Project documentation
```

### Detailed Breakdown of Key Modules

#### `backend/app/parser.py`
- **Purpose**: Static inspection of Python code using Python's native `ast` library.
- **Responsibility**: Parses Python source text into an Abstract Syntax Tree. Identifies all top-level functions, classes, methods, argument lists, type annotations, default parameters, variable/keyword arguments (`*args`, `**kwargs`), docstrings, exact line numbers (`lineno`, `end_lineno`), top-level and nested return expressions, and all exceptions explicitly thrown via `raise` statements.
- **Key Functions**:
  - `scan_code(source_code: str) -> Dict[str, Any]`: High-level entry point parsing code into `{classes, functions, imports}`.
  - `parse_function_node(node: ast.FunctionDef | ast.AsyncFunctionDef) -> Dict[str, Any]`: Extracts arguments, return types, return expressions, and raised exceptions.
  - `_find_return_expr(body_nodes: list) -> str | None`: Scans backwards through body nodes recursively to capture return expressions.
  - `_find_raised_exceptions(body_nodes: list) -> list[str]`: Recursively collects exception types raised inside function bodies.

#### `backend/app/generator.py`
- **Purpose**: AST-driven automated PyTest suite generation.
- **Responsibility**: Converts the metadata extracted by `parser.py` into a complete, executable, syntax-valid PyTest Python file.
- **Key Functions**:
  - `generate_test_template(filename, parsed_structure, project_class_map, source_code) -> str`: Builds PyTest modules complete with dependency imports, class fixtures, constructor mocks, function tests, method tests, dataclass field assertions, and negative tests verifying AST-discovered `raise` statements.
  - `get_smart_default_value(annotation: str, field_name: str) -> str`: Infers semantic dummy test values based on parameter name and type (e.g., `id -> 101`, `stock -> 10`, `email -> "john@example.com"`, `price -> 50000.0`, `List[T] -> []`).
  - `resolve_arg_value()`: Recursively maps function parameters to required fixtures or semantic values, registering cross-file module imports.

#### `backend/app/gemini.py`
- **Purpose**: LLM client configuration, prompt engineering, and response sanitization.
- **Responsibility**: Interfaces with Google Generative AI to suggest edge cases for specific AST nodes. Enforces strict instruction prompts (8 strict rules) and implements fallback mechanisms (Gemini 2.5 Pro with automatic fallback to Gemini 2.5 Flash on HTTP 429 / quota exhaustion).
- **Key Functions**:
  - `suggest_edge_cases(...)`: Prompts the model with the target function/class alongside full file context, requiring raw JSON responses.
  - `_clean_generated_code(...)`: Post-processes generated code by detecting and stripping duplicate class definitions (`class Product:`) and ensuring required source imports exist at the top of the file.

#### `backend/app/executor.py`
- **Purpose**: Secure sandboxed test runner.
- **Responsibility**: Spawns an isolated temporary folder under `backend/temp_runs/<uuid>`, writes out source and test files, executes `pytest` with coverage instrumentation via Python's `subprocess.run`, parses generated JUnit XML and Coverage.py JSON reports, and guarantees filesystem cleanup in a `finally` block.
- **Key Functions**:
  - `execute_tests(project_files, test_files) -> Dict[str, Any]`: Executes `python -m pytest --junitxml=report.xml --cov=. --cov-report=json -v` in the sandbox with a 30-second safety timeout.
  - `parse_junit_xml(xml_path) -> Dict[str, Any]`: Extracts passed, failed, errored, and skipped test case counts, timings, and failure stack traces.
  - `parse_coverage_json(json_path) -> Dict[str, Any]`: Computes total statement coverage percentage and maps executed vs missing lines per file.

#### `scripts/testforge_scanner.py`
- **Purpose**: Platform-independent CLI scanner for CI/CD pipelines.
- **Responsibility**: Runs `git diff` against a target branch (e.g., `origin/main`), detects changed line numbers, reads `coverage.json`, identifies functions with missing test coverage on changed lines, calculates Cyclomatic Complexity and modification frequency, computes a weighted **Risk Score**, optionally prompts Gemini for test recommendations, and comments the markdown report onto the GitHub Pull Request using GitHub's REST API with comment-updating anti-spam logic.

---

## 3. APPLICATION ARCHITECTURE

### Architecture Diagram

```
                     ┌────────────────────────────────────────────────────────┐
                     │                       USER BROWSER                     │
                     │  (Next.js 16 App Router · TypeScript · Tailwind CSS 4) │
                     └───────────────┬────────────────────────▲───────────────┘
                                     │                        │
                      HTTP / HTTPS   │ Authorization: Bearer  │ JSON / CSV
                                     ▼                        │
                     ┌────────────────────────────────────────┴───────────────┐
                     │               FASTAPI ASGI BACKEND (Uvicorn)           │
                     │  app/main.py · CORS Middleware · Exception Handlers    │
                     └───────┬───────────────────┬────────────────────┬───────┘
                             │                   │                    │
              ┌──────────────┴──────┐     ┌──────┴─────────────┐      │
              │  AUTH & SECURITY    │     │  ROUTERS & APIS    │      │
              │  - app/auth.py      │     │  - /api/projects   │      │
              │  - PBKDF2 Hashing   │     │  - /api/tests      │      │
              │  - JWT Bearer (HS256)     │  - /api/ai         │      │
              │  - OAuth2 Dependency│     │  - /api/testcases  │      │
              └──────────────┬──────┘     └──────┬─────────────┘      │
                             │                   │                    │
                             ▼                   ▼                    │
                     ┌─────────────────────────────────────────┐      │
                     │             CORE ENGINES                │      │
                     │  1. parser.py   (AST Static Scanning)   │      │
                     │  2. generator.py (PyTest Code Synthesis)│      │
                     │  3. executor.py (Sandboxed Runner)      │      │
                     │  4. gemini.py   (LLM Sanitization)      │      │
                     └───────┬───────────────────┬─────────────┘      │
                             │                   │                    │
                 Subprocess  │                   │ Google API         │
                 Execution   │                   │ (gemini-2.5-flash) │
                             ▼                   ▼                    │
                     ┌──────────────┐     ┌──────────────┐            │
                     │ TEMP SANDBOX │     │  GEMINI LLM  │            │
                     │ (temp_runs/) │     │  AI Copilot  │            │
                     │ pytest --cov │     └──────────────┘            │
                     └───────┬──────┘                                 │
                             │ XML & JSON Reports                     │
                             ▼                                        ▼
                     ┌────────────────────────────────────────────────────────┐
                     │              DATA PERSISTENCE LAYER                    │
                     │  SQLAlchemy ORM · SQLite Database (testforge.db)       │
                     │  Users | Projects | ProjectFiles | GeneratedTests      │
                     │  TestRuns | TestCases | TestData                       │
                     └────────────────────────────────────────────────────────┘

    ─────────────────────────────────────────────────────────────────────────
    SEPARATE CI/CD PIPELINE (GitHub Actions)
    git push / pull_request → .github/workflows/testforge_ci.yml
         ↓
    pytest backend/app --cov=backend/app --cov-report=json:coverage.json
         ↓
    python scripts/testforge_scanner.py --coverage coverage.json --diff origin/main --publish
         ↓
    GitHub REST API → Automatically posts/updates PR Quality Intelligence Comment
```

### Architectural Principles Implemented
1. **Decoupled Client-Server**: Frontend (Next.js) communicates exclusively with Backend (FastAPI) via structured REST endpoints over HTTP with JWT authentication.
2. **Execution Safety through AST**: User-uploaded Python code is analyzed using standard library `ast.parse` rather than dynamic `importlib` or `eval()`, preventing malicious code execution during analysis.
3. **Sandbox Isolation**: When tests are executed, code is written to unique transient UUID directories under `backend/temp_runs/`. The subprocess runs with a strict 30-second timeout, and the directory is destroyed immediately upon completion.
4. **Resilient LLM Integration**: Implements model fallback (`gemini-2.5-pro` -> `gemini-2.5-flash`), markdown stripping, and regex-based AST AST sanitization to ensure AI outputs do not break test execution.

---

## 4. FRONTEND ARCHITECTURE

### 4.1 Framework & Configuration
- **Framework**: Next.js 16.2.6 using the modern **App Router** paradigm (`src/app/`).
- **Language**: TypeScript 5 with strict compiler options (`"strict": true` in `tsconfig.json`).
- **Styling**: Tailwind CSS v4 configured with `@tailwindcss/postcss`. Custom dark glassmorphism effects are defined in `src/app/globals.css` using utility classes:
  - `.glass-card`: `bg-gray-950/60 backdrop-blur-xl border border-gray-800/80`
  - `.glass-card-hover`: `hover:border-indigo-500/30 hover:bg-gray-900/40`
  - `.badge-pass` / `.badge-fail` / `.badge-running` for test execution statuses.
- **Icons**: Lucide React.
- **Charts**: Recharts (`^3.8.1`).

### 4.2 State Management & Network Layer
- **No Heavy External State Stores**: Avoided Redux or Zustand. The application relies on React's native hooks (`useState`, `useEffect`, `use`) alongside localized state hoisting.
- **Centralized API Client (`src/lib/api.ts`)**:
  - `API_BASE`: Defaults to `process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api"`.
  - `getAuthHeaders()`: Reads `token` from `localStorage` and injects `Authorization: Bearer <token>`.
  - `apiRequest(path, options)`: Automatically sets `Content-Type: application/json` (unless body is `FormData`), executes `fetch`, intercepts HTTP 401 Unauthorized responses, clears `localStorage`, and redirects the user to `/login`. Handles HTTP 204 No Content gracefully.

### 4.3 Page Details & User Interactions

#### 1. Login Page (`src/app/login/page.tsx`)
- **Route**: `/login`
- **Interactions**: User inputs email and password. Submits JSON to `POST /api/auth/login/json`.
- **State**: `email`, `password`, `error`, `loading`.
- **Token Handling**: Clears pre-existing token on mount; stores received `access_token` into `localStorage.setItem("token", data.access_token)` on success; navigates to `/`.

#### 2. Registration Page (`src/app/register/page.tsx`)
- **Route**: `/register`
- **Interactions**: Inputs email, password, and confirm password. Validates password equality client-side.
- **State**: `email`, `password`, `confirmPassword`, `error`, `success`, `loading`.
- **API Call**: `POST /api/auth/register`. On success, displays confirmation and redirects to `/login` after 1.5 seconds.

#### 3. Dashboard Page (`src/app/page.tsx`)
- **Route**: `/`
- **Interactions**: Fetches user profile (`GET /api/auth/me`) and project list (`GET /api/projects/`). Shows summary metrics (Total Projects, AST Engine Stack, PyTest status). Allows opening modal to create new projects (`POST /api/projects/`) or deleting projects (`DELETE /api/projects/{id}`).
- **Navigation**: Clicking any project card routes to `/projects/[id]`.

#### 4. Dual-Mode Project Workspace (`src/app/projects/[id]/page.tsx`)
- **Route**: `/projects/[id]` (1,350 lines of TypeScript code)
- **Mode Toggle**: Controls workspace behavior via `workspaceMode`:
  - `"unit"`: Unit & Code Testing Mode
  - `"qa"`: QA Automation & Test Cases Mode

##### In Unit Mode (`workspaceMode === 'unit'`):
- **Left Column (Project Files & AST Tree)**:
  - File uploader accepts `.py` files via multi-part upload (`POST /api/projects/{id}/upload`).
  - Lists uploaded files. Selecting a file loads content (`GET /api/projects/{id}/files/{file_id}/content`) and parsed AST analysis (`classes`, `functions`, `imports`).
  - Clicking a Class or Function AST node selects it and automatically invokes `POST /api/ai/recommend`.
- **Center Column (Code Editor & Tabs)**:
  - Dual tabs: **Source Code** (read-only syntax view) vs **Generated PyTest** (live editable textarea).
  - Automatically fetches or generates the initial PyTest template (`GET /api/tests/{id}/generate?filename=...`).
  - Allows saving edited test content (`POST /api/tests/{id}/save`).
  - "Execute PyTest Suite" button triggers `POST /api/tests/{id}/run`, saves current test content, displays live status banner, and updates run history.
- **Right Column (Gemini Edge Cases vs Execution History)**:
  - When an AST node is selected: Renders **Gemini Edge Cases** cards with title, explanation, and code block. Has two buttons: **Copy Code** and **Add to Test Suite (`+`)**.
  - Deduplication & Auto-Rename Logic (`handleAppendTest`): When appending AI test code, it regex-detects test function names (`def test_...`), inspects current editor content, and automatically appends numerical suffixes (`test_func_1`, `test_func_2`) to prevent duplicate function name collisions in PyTest. Strips redundant top-level `import` statements before appending.
  - When no AST node is selected: Shows **Execution History** list of past runs (`GET /api/tests/{id}/runs`) with status badges, timestamps, coverage percentage, and links to `/projects/[id]/runs/[run_id]`.

##### In QA Mode (`workspaceMode === 'qa'`):
- **Left Column (Test Case Repository)**:
  - Table displaying `Title`, `Steps`, `Expected Result`, and Actions.
  - "Download Template" triggers client-side CSV template generation.
  - "Import CSV" uploads CSV via `POST /api/testcases/{id}/import`.
  - "Export CSV" downloads all project test cases via `GET /api/testcases/{id}/export`.
  - "Add Test Case" opens a modal submitting `POST /api/testcases/{id}`.
- **Middle Column (Externalized Test Data)**:
  - Lists project configuration parameters (`key`, `value`, `description`).
  - Inline form submits `POST /api/testcases/{id}/testdata` (e.g. `BASE_URL = http://localhost:3000`).
  - Parameters are deleted via `DELETE /api/testcases/{id}/testdata/{id}`.
- **Right Column (Playwright Automation Generator)**:
  - Clicking "Automate" on any test case triggers `POST /api/testcases/{id}/generate-automation/{tc_id}`.
  - Gemini translates manual steps and injects defined externalized variables into an executable Playwright Python script.
  - Displays generated script in a code container with a one-click copy button.

#### 5. Run Report Page (`src/app/projects/[id]/runs/[run_id]/page.tsx`)
- **Route**: `/projects/[id]/runs/[run_id]`
- **Interactions**: Fetches run data (`GET /api/tests/{id}/runs/{run_id}`).
- **Left Sidebar**: Renders KPI cards for Success Pass Rate percentage bar, Total Code Coverage percentage bar, and Passed vs Failed test counts.
- **Tabbed Right Workspace**:
  - **Test Cases Tab**: Interactive list of all executed tests parsed from JUnit XML with execution time in seconds. Failed/errored tests are expandable to reveal full stack traces and assertion failure messages.
  - **Coverage Breakdown Tab**: Lists every project Python source file with statement counts, percent covered progress bars (color-coded: green $\ge 80\%$, yellow $\ge 50\%$, red $< 50\%$), and explicit tags for every **Missing Line Number**.
  - **Terminal Outputs Tab**: Displays raw `stdout` and `stderr` terminal logs captured during test execution with a "Copy Console Log" button.

---

## 5. BACKEND ARCHITECTURE

### 5.1 Runtime & Entry Point
- **Runtime**: Python 3.10+ ASGI application.
- **Entry Point**: `backend/app/main.py`
- **Application Initialization**:
  - Automatically initializes SQLite tables on startup: `Base.metadata.create_all(bind=engine)`
  - Configures `CORSMiddleware` with comprehensive allowed origins:
    - `http://localhost:3000`, `3001`, `3002`
    - `http://127.0.0.1:3000`, `3001`, `3002`
    - `https://testforge-ai-lime.vercel.app`
    - `https://testforge.chiragvasava.me`
    - Dynamically parses `ALLOWED_ORIGINS`, `ALLOWED_ORIGIN`, and `FRONTEND_URL` from environment variables.
  - Mounts routers under `/api`:
    - `app.include_router(auth.router, prefix="/api")`
    - `app.include_router(projects.router, prefix="/api")`
    - `app.include_router(tests.router, prefix="/api")`
    - `app.include_router(ai.router, prefix="/api")`
    - `app.include_router(testcases.router, prefix="/api")`

### 5.2 Complete API Reference

#### Authentication Endpoints (`app/routers/auth.py`)

| Method | Endpoint | Description | Auth Required | Request Body | Response | Error Codes |
|---|---|---|---|---|---|---|
| `POST` | `/api/auth/register` | Register new user | No | `UserCreate` (`email`, `password`) | `UserResponse` (`id`, `email`, `created_at`) | 400 (Email exists), 422 (Validation) |
| `POST` | `/api/auth/login` | OAuth2 form login | No | `OAuth2PasswordRequestForm` (form-data) | `Token` (`access_token`, `token_type`) | 401 (Invalid credentials) |
| `POST` | `/api/auth/login/json` | JSON payload login | No | `JsonLoginRequest` (`email`, `password`) | `Token` (`access_token`, `token_type`) | 401 (Invalid credentials) |
| `GET` | `/api/auth/me` | Fetch active user | Yes (Bearer) | None | `UserResponse` (`id`, `email`, `created_at`) | 401 (Unauthorized) |

#### Project Management Endpoints (`app/routers/projects.py`)

| Method | Endpoint | Description | Auth Required | Request Body / Params | Response | Error Codes |
|---|---|---|---|---|---|---|
| `POST` | `/api/projects/` | Create project | Yes (Bearer) | `ProjectCreate` (`name`, `description`) | `ProjectResponse` | 401, 422 |
| `GET` | `/api/projects/` | List user projects | Yes (Bearer) | None | `List[ProjectResponse]` | 401 |
| `GET` | `/api/projects/{project_id}` | Get project | Yes (Bearer) | Path `project_id: int` | `ProjectResponse` | 401, 404 |
| `DELETE`| `/api/projects/{project_id}` | Delete project | Yes (Bearer) | Path `project_id: int` | 204 No Content | 401, 404 |
| `POST` | `/api/projects/{project_id}/upload` | Upload & AST scan file | Yes (Bearer) | Multipart `file: UploadFile` | `{file: {...}, analysis: {classes, functions, imports}}` | 400 (Non-UTF8), 401, 404 |
| `GET` | `/api/projects/{project_id}/files` | List project files | Yes (Bearer) | Path `project_id: int` | `List[ProjectFileResponse]` | 401, 404 |
| `GET` | `/api/projects/{project_id}/files/{file_id}/content` | Get source content | Yes (Bearer) | Path `project_id`, `file_id` | `{filename: str, content: str}` | 401, 404 |
| `GET` | `/api/projects/{project_id}/structure` | Full project AST | Yes (Bearer) | Path `project_id: int` | `{<filename>: {classes, functions, imports}}` | 401, 404 |

#### Unit Testing & Execution Endpoints (`app/routers/tests.py`)

| Method | Endpoint | Description | Auth Required | Request Body / Params | Response | Error Codes |
|---|---|---|---|---|---|---|
| `GET` | `/api/tests/{project_id}/generate` | Generate PyTest template | Yes (Bearer) | Query `filename: str` | `{filename: str, content: str, scanned_item_name: str}` | 400 (AST syntax error), 401, 404 |
| `POST` | `/api/tests/{project_id}/save` | Save PyTest file | Yes (Bearer) | `GeneratedTestCreate` (`filename`, `content`, `scanned_item_name`) | `GeneratedTestResponse` | 401, 404 |
| `GET` | `/api/tests/{project_id}/generated` | List saved tests | Yes (Bearer) | Path `project_id: int` | `List[GeneratedTestResponse]` | 401, 404 |
| `POST` | `/api/tests/{project_id}/run` | Execute tests in sandbox | Yes (Bearer) | Path `project_id: int` | `TestRunResponse` (`id`, `status`, `passed_count`, `failed_count`, `coverage_percentage`, `stdout_logs`, `coverage_report`) | 400 (No files/tests), 401, 404 |
| `GET` | `/api/tests/{project_id}/runs` | List test runs | Yes (Bearer) | Path `project_id: int` | `List[TestRunResponse]` | 401, 404 |
| `GET` | `/api/tests/{project_id}/runs/{run_id}` | Get run report | Yes (Bearer) | Path `project_id`, `run_id` | `TestRunResponse` | 401, 404 |

#### AI Copilot Endpoints (`app/routers/ai.py`)

| Method | Endpoint | Description | Auth Required | Request Body | Response | Error Codes |
|---|---|---|---|---|---|---|
| `POST` | `/api/ai/recommend` | Gemini edge cases | Yes (Bearer) | `RecommendationRequest` (`file_id`, `name`, `element_type`) | `{suggestions: [{title, explanation, test_code}]}` | 401, 403, 404, 500 |

#### QA Test Cases & Automation Endpoints (`app/routers/testcases.py`)

| Method | Endpoint | Description | Auth Required | Request Body / Params | Response | Error Codes |
|---|---|---|---|---|---|---|
| `GET` | `/api/testcases/{project_id}` | List test cases | Yes (Bearer) | Path `project_id: int` | `List[TestCaseResponse]` | 401, 404 |
| `POST` | `/api/testcases/{project_id}` | Create test case | Yes (Bearer) | `TestCaseCreate` (`title`, `description`, `steps`, `expected_result`, `test_data`) | `TestCaseResponse` | 401, 404 |
| `DELETE`| `/api/testcases/{project_id}/{testcase_id}` | Delete test case | Yes (Bearer) | Path `project_id`, `testcase_id` | 204 No Content | 401, 404 |
| `POST` | `/api/testcases/{project_id}/import` | Import test cases CSV | Yes (Bearer) | Multipart `file: UploadFile` | `{message: str, errors: list}` | 400 (CSV header/format), 401, 404 |
| `GET` | `/api/testcases/{project_id}/export` | Export test cases CSV | Yes (Bearer) | Path `project_id: int` | `StreamingResponse` (text/csv) | 401, 404 |
| `POST` | `/api/testcases/{project_id}/generate-automation/{testcase_id}` | Playwright script gen | Yes (Bearer) | Path `project_id`, `testcase_id` | `{script: str}` | 401, 404, 500 |
| `GET` | `/api/testcases/{project_id}/testdata` | List test variables | Yes (Bearer) | Path `project_id: int` | `List[TestDataResponse]` | 401, 404 |
| `POST` | `/api/testcases/{project_id}/testdata` | Create/update variable | Yes (Bearer) | `TestDataCreate` (`key`, `value`, `description`) | `TestDataResponse` | 401, 404 |
| `DELETE`| `/api/testcases/{project_id}/testdata/{data_id}` | Delete test variable | Yes (Bearer) | Path `project_id`, `data_id` | 204 No Content | 401, 404 |

---

## 6. DATABASE ARCHITECTURE

### 6.1 Database Engine & Session Management
- **Database**: SQLite (`testforge.db`) locally.
- **ORM**: SQLAlchemy (declarative base).
- **Thread Safety**: SQLite handles single-thread writes; `connect_args={"check_same_thread": False}` is configured in `backend/app/database.py` to permit FastAPI's asynchronous thread pool workers to share the engine.
- **Session Lifecycle**: `get_db()` yields a `SessionLocal` instance per HTTP request and guarantees closure in a `finally` block:
  ```python
  def get_db():
      db = SessionLocal()
      try:
          yield db
      finally:
          db.close()
  ```
- **PostgreSQL Readiness**: `database.py` checks `DATABASE_URL`. If the URL does not start with `sqlite`, it connects cleanly to PostgreSQL without `connect_args`.

### 6.2 Relational Schema & Entity Relationship Diagram

```
       ┌────────────────────────┐
       │         User           │
       ├────────────────────────┤
       │ id: Integer (PK)       │
       │ email: String (Unique) │
       │ hashed_password: String│
       │ created_at: DateTime   │
       └───────────┬────────────┘
                   │ 1
                   │
                   │ owns (cascade delete)
                   │
                   │ N
       ┌───────────▼────────────┐
       │        Project         │
       ├────────────────────────┤
       │ id: Integer (PK)       │
       │ name: String           │
       │ description: String    │
       │ owner_id: Integer (FK) │
       │ created_at: DateTime   │
       └─────┬───┬────┬───┬───┬─┘
             │   │    │   │   │
  ┌──────────┘   │    │   │   └──────────┐
  │ 1            │ 1  │ 1 │ 1            │ 1
  │              │    │   │              │
  ▼ N            │    │   │              ▼ N
┌──────────────┐ │    │   │   ┌────────────────────┐
│ ProjectFile  │ │    │   │   │      TestData      │
├──────────────┤ │    │   │   ├────────────────────┤
│ id (PK)      │ │    │   │   │ id (PK)            │
│ project_id   │ │    │   │   │ project_id (FK)    │
│ filename     │ │    │   │   │ key: String        │
│ content: Text│ │    │   │   │ value: String      │
│ created_at   │ │    │   │   │ description: String│
└──────────────┘ │    │   │   │ created_at         │
                 │    │   │   └────────────────────┘
                 ▼ N  │   ▼ N
┌───────────────────┐ │ ┌───────────────────┐
│   GeneratedTest   │ │ │     TestCase      │
├───────────────────┤ │ ├───────────────────┤
│ id (PK)           │ │ │ id (PK)           │
│ project_id (FK)   │ │ │ project_id (FK)   │
│ filename: String  │ │ │ title: String     │
│ content: Text     │ │ │ description: Text │
│ scanned_item_name │ │ │ steps: Text       │
│ created_at        │ │ │ expected_result   │
└───────────────────┘ │ │ test_data: Text   │
                      │ │ created_at        │
                      │ └───────────────────┘
                      ▼ N
         ┌───────────────────────────┐
         │          TestRun          │
         ├───────────────────────────┤
         │ id (PK)                   │
         │ project_id (FK)           │
         │ status: String            │
         │ passed_count: Integer     │
         │ failed_count: Integer     │
         │ coverage_percentage: Float│
         │ stdout_logs: Text         │
         │ coverage_report: TextJSON │
         │ created_at: DateTime      │
         └───────────────────────────┘
```

### 6.3 Relational Details & Constraints
- `users`: Primary key `id`. Index on `email` (unique). Cascade deletes all owned `projects`.
- `projects`: Primary key `id`. Index on `name`. Foreign key `owner_id -> users.id` with `ondelete="CASCADE"`. Cascade deletes child files, tests, runs, test cases, and test data.
- `project_files`: Foreign key `project_id -> projects.id`. Stores raw Python source in `content: Text`.
- `generated_tests`: Foreign key `project_id -> projects.id`. Stores synthesized PyTest code in `content: Text`.
- `test_runs`: Foreign key `project_id -> projects.id`. Stores summary metrics (`status`, `passed_count`, `failed_count`, `coverage_percentage`), console output (`stdout_logs`), and complete JUnit/coverage data formatted as JSON in `coverage_report: Text`.
- `test_cases`: Foreign key `project_id -> projects.id`. Stores plain-English manual test steps, expected results, and optional JSON variables.
- `test_data`: Foreign key `project_id -> projects.id`. Stores uppercase key-value pairs representing externalized environment parameters.

---

## 7. COMPLETE USER FLOWS

### Flow 1: User Registration & Authentication
```
User (Browser)
  │ Fill out form: email + password
  ▼
frontend/src/app/register/page.tsx
  │ Validate password === confirmPassword
  ▼
POST /api/auth/register
  │ backend/app/routers/auth.py -> register()
  ▼
backend/app/auth.py -> get_password_hash()
  │ Generate 16-byte random salt: secrets.token_hex(16)
  │ PBKDF2-HMAC-SHA256 with 100,000 iterations
  │ Returns "salt:hex_hash"
  ▼
SQLAlchemy: models.User stored in SQLite
  ▼
Redirect to /login -> Fill credentials -> POST /api/auth/login/json
  ▼
backend/app/auth.py -> verify_password()
  │ Split stored password into salt and original key
  │ Re-hash incoming password with salt and compare using secrets.compare_digest
  ▼
backend/app/auth.py -> create_access_token()
  │ Sign JWT payload {"sub": email, "exp": now + 1440 mins} using config.SECRET_KEY
  ▼
Frontend receives access_token -> Stores in localStorage.setItem("token", ...)
  ▼
Router pushes to Dashboard (/)
```

### Flow 2: Python File Upload & AST Analysis
```
User uploads "bank_account.py" in /projects/[id]
  ▼
frontend/src/app/projects/[id]/page.tsx -> handleFileUpload()
  │ Appends File to FormData
  ▼
POST /api/projects/{project_id}/upload
  │ backend/app/routers/projects.py -> upload_file()
  │ Authenticates user via Depends(auth.get_current_user)
  │ Verifies project ownership (project.owner_id == current_user.id)
  │ Decodes file bytes as UTF-8
  │ Upserts file content into models.ProjectFile
  ▼
backend/app/parser.py -> scan_code(content)
  │ ast.parse(source_code)
  │ Traverses ast.walk / body nodes:
  │   - ast.ClassDef -> extracts bases, fields, methods
  │   - ast.FunctionDef -> extracts arguments, default values, type annotations, return expressions, raised exceptions
  │   - ast.Import / ast.ImportFrom -> extracts import statements
  ▼
Returns JSON response: { file: {...}, analysis: { classes: [...], functions: [...], imports: [...] } }
  ▼
Frontend populates Left Sidebar AST tree with classes (C) and functions (F)
```

### Flow 3: PyTest Template Generation
```
Frontend calls GET /api/tests/{project_id}/generate?filename=bank_account.py
  ▼
backend/app/routers/tests.py -> generate_tests_for_file()
  │ Reads target ProjectFile content
  │ Scans target file AST: scan_code(content)
  │ Queries all sibling ProjectFiles in project to construct project_class_map (cross-file registry)
  ▼
backend/app/generator.py -> generate_test_template()
  │ 1. Fixture Dependency Graph:
  │    - Traverses classes, identifies constructor parameters
  │    - Excludes ABCs, Exceptions, and Enums from fixture generation
  │    - Generates @pytest.fixture functions with dependency injection
  │ 2. Parameter Mapping:
  │    - Inspects type annotations and argument names
  │    - Injects smart defaults (e.g., amount -> 50000.0, email -> "john@example.com")
  │ 3. Method Assertions:
  │    - Parses return expressions (int, bool, float, str, None) to produce semantic assertions
  │ 4. Negative Exception Tests:
  │    - For every AST-detected `raise ErrorType`, generates `with pytest.raises(ErrorType):` test
  ▼
Returns { filename: "test_bank_account.py", content: "<pytest code>", ... }
  ▼
Frontend populates in-browser editable code editor
```

### Flow 4: Gemini AI Edge Case Generation & Injection
```
User clicks class "BankAccount" or method "withdraw" in AST Tree
  ▼
frontend/src/app/projects/[id]/page.tsx -> handleSelectElement("withdraw", "function")
  ▼
POST /api/ai/recommend
  │ Body: { file_id: 12, name: "withdraw", element_type: "function" }
  │ Authenticates user & checks project ownership
  ▼
backend/app/gemini.py -> suggest_edge_cases()
  │ Extracts source file imports via _extract_imports_from_source()
  │ Builds prompt with 8 strict rules (no class redefinitions, no fake imports, meaningful assertions only)
  │ Calls Gemini API (attempts gemini-2.5-pro; on 429 rate limit, falls back to gemini-2.5-flash)
  │ Cleans response via _clean_generated_code() (strips duplicate classes and ensures valid imports)
  ▼
Returns JSON: { suggestions: [ { title: "Insufficient Funds", explanation: "...", test_code: "..." } ] }
  ▼
Frontend renders AI Suggestion cards
  ▼
User clicks "+" button on suggestion card
  ▼
frontend/src/app/projects/[id]/page.tsx -> handleAppendTest()
  │ Regex scans for `def test_...` names
  │ Checks for collisions against existing editor code
  │ Auto-renames duplicates (e.g. `test_withdraw_insufficient_funds_1`)
  │ Strips redundant `import` lines
  │ Appends cleaned test block to editor content
```

### Flow 5: Sandboxed PyTest Execution & Reporting
```
User clicks "Execute PyTest Suite"
  ▼
frontend/src/app/projects/[id]/page.tsx -> handleRunTests()
  │ Auto-saves current editor test content to DB via POST /api/tests/{id}/save
  ▼
POST /api/tests/{project_id}/run
  │ backend/app/routers/tests.py -> run_project_tests()
  │ Queries all ProjectFiles and GeneratedTests for project
  ▼
backend/app/executor.py -> execute_tests()
  │ Creates temp directory: backend/temp_runs/<uuid>/
  │ Writes all source files (.py) and test files (.py) to temp directory
  │ Resolves virtualenv python: backend/.venv/Scripts/python.exe (or sys.executable)
  │ Spawns subprocess:
  │   python -m pytest --junitxml=report.xml --cov=. --cov-report=json -v (30s timeout)
  │ Reads and parses report.xml (passed, failed, timings, stack traces)
  │ Reads and parses coverage.json (percent_covered, missing_lines, executed_lines)
  │ Finally block: shutil.rmtree(run_dir) guarantees cleanup
  ▼
backend/app/routers/tests.py stores models.TestRun in SQLite
  ▼
Frontend receives TestRun response -> Updates run history
  ▼
User clicks Run -> Routes to /projects/[id]/runs/[run_id]
  ▼
Visualizes Success Rate (%), Coverage (%), Test Cases breakdown, and Missing Lines
```

### Flow 6: QA Manual Cases & Playwright Script Generation
```
User switches workspaceMode to "qa"
  ▼
Import CSV (or enter manual test case via form):
  - title: "User Checkout"
  - steps: "1. Go to /cart\n2. Click checkout\n3. Fill address"
  - expected_result: "Order confirmation displayed"
  ▼
User adds Externalized Variable in Test Data panel:
  - Key: "BASE_URL", Value: "http://localhost:3000"
  ▼
User clicks "Automate 🪄" on test case
  ▼
POST /api/testcases/{project_id}/generate-automation/{testcase_id}
  │ backend/app/routers/testcases.py -> generate_automation_script()
  │ Queries all project TestData key-value pairs
  │ Constructs prompt for Gemini with test case details and externalized variables dictionary
  │ Configures Gemini 2.5 Flash
  │ Prompts model to generate pure Playwright Python code with sync/async API, page locators, and expect assertions
  │ Strips markdown code blocks
  ▼
Returns JSON: { script: "from playwright.sync_api import sync_playwright, expect\n..." }
  ▼
Frontend displays syntax-highlighted Playwright script with one-click clipboard copy
```

---

## 8. AUTHENTICATION & SECURITY

### 8.1 Password Hashing Implementation
- **Implementation Location**: `backend/app/auth.py`
- **Technique**: Custom, standard-library implementation using **PBKDF2 with HMAC-SHA256**.
- **Implementation Detail**:
  ```python
  salt = secrets.token_hex(16)
  key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
  return f"{salt}:{key.hex()}"
  ```
- **Password Verification**: Splits the stored string into `salt` and `key_hex`, re-runs PBKDF2 with the salt, and performs constant-time equality validation using `secrets.compare_digest(new_key.hex(), key_hex)` to prevent timing attacks.
- **Architectural Rationale**: Although `passlib[bcrypt]` is present in `requirements.txt`, using Python's native `hashlib` and `secrets` eliminates native binary compilation issues across different operating systems (especially Windows and Alpine Linux).

### 8.2 Token Architecture & Protected Routes
- **Algorithm**: `HS256` (HMAC with SHA-256).
- **Secret Key**: Configured in `backend/.env` as `SECRET_KEY`, falling back to a default development string in `config.py`.
- **Token Expiry**: Configured via `ACCESS_TOKEN_EXPIRE_MINUTES` (defaults to 1,440 minutes / 24 hours).
- **OAuth2 Scheme**: `OAuth2PasswordBearer(tokenUrl="api/auth/login")`.
- **Dependency Injection (`get_current_user`)**:
  - Injected into protected routes via `Depends(auth.get_current_user)`.
  - Decodes token using `jose.jwt.decode`.
  - Validates `sub` claim containing the user's email.
  - Queries `models.User` from the database. If not found or invalid, raises `HTTPException(status_code=401, detail="Could not validate credentials")`.

### 8.3 Authorization & Data Isolation
- Every project-scoped API endpoint checks user ownership before executing operations:
  ```python
  project = db.query(models.Project).filter(
      models.Project.id == project_id,
      models.Project.owner_id == current_user.id
  ).first()
  if not project:
      raise HTTPException(status_code=404, detail="Project not found")
  ```
- Users cannot access, modify, upload files to, or execute tests on another user's project.

### 8.4 Subprocess Execution Security
- **Untrusted Code Risk**: Executing arbitrary Python code submitted via a web interface poses severe remote execution risks.
- **Mitigation in TestForge AI**:
  1. Static analysis (`parser.py`) uses `ast.parse` which does not execute code.
  2. Subprocess execution in `executor.py` runs inside an isolated temporary directory created with `uuid.uuid4().hex`.
  3. Strict subprocess timeout of 30 seconds (`timeout=30`) prevents infinite loops or fork bombs from hanging the server.
  4. Cleanup in `finally: shutil.rmtree(run_dir, ignore_errors=True)` ensures no lingering scripts or artifacts remain on disk.

---

## 9. IMPORTANT CODE EXPLANATIONS

### 9.1 `backend/app/generator.py`: AST Fixture & Test Builder

#### What It Does:
Generates an entire PyTest module file from raw AST metadata without executing the source file.

#### How It Works:
1. **Module Name Cleaning**: Extracts base name (`utils.py` -> `utils`).
2. **Class & Function Separation**: Collects target file classes, functions, and cross-file classes registered in `project_class_map`.
3. **Fixture Dependency Graph Traversal (BFS)**:
   - Identifies which classes need test fixtures, explicitly filtering out Abstract Base Classes (`ABC`), exception classes, and enum classes.
   - Inspects `__init__` constructor parameters. If a parameter's type annotation matches another known class, it automatically enqueues that dependency and generates a dedicated `@pytest.fixture` with constructor injection.
4. **Smart Default Value Resolution (`get_smart_default_value`)**:
   - Maps annotations and variable names to realistic test inputs (`id -> 101`, `quantity -> 2`, `price -> 50000.0`, `email -> "john@example.com"`, `List[T] -> []`, `Dict -> {}`).
5. **Assertion Inference**:
   - Inspects AST return expressions:
     - Returns numbers (`re.match(r'^\d+(\.\d+)?$', ret)`): `assert result == <num>`
     - Returns boolean (`True`/`False`): `assert result is True/False`
     - Returns `None`: `assert result is None`
     - Returns strings: `assert result == <str>`
     - Semantic method heuristics: methods containing `discount_rate` assert `isinstance(result, float)`, methods containing `checkout` assert `result.status == BookStatus.BORROWED`.
6. **Negative Exception Testing**:
   - If an AST method contains `raise ValueError`, it generates a negative test invoking the method with invalid parameters (`-1`, `invalid-email`) wrapped inside `with pytest.raises(ValueError):`.

### 9.2 `backend/app/gemini.py`: Prompt Engineering & AST Code Cleaning

#### What It Does:
Generates high-value edge cases from Gemini while correcting common LLM code-generation mistakes.

#### How It Works:
1. **Context Extraction**:
   - Parses the target file with AST to extract existing imports (`_extract_imports_from_source`) and existing class/function names (`_extract_defined_names_from_source`).
2. **Prompt Constraints (8 Rules)**:
   - Rule 1: Never redefine classes from the source file.
   - Rule 2: Never add unnecessary standard imports.
   - Rule 3: Meaningful assertions only (strictly forbids `assert True`, `assert x == x`).
   - Rule 4: Valid constructor calls only (infer realistic fields).
   - Rule 5: Use `@pytest.mark.parametrize` for similar inputs.
   - Rule 6: Use `pytest.raises` for exception paths.
   - Rule 7: Descriptive snake_case names.
   - Rule 8: Test behavior, not Python language defaults.
3. **Code Post-Processing (`_clean_generated_code`)**:
   - LLMs frequently copy the source class into the test file. `_clean_generated_code` parses lines, detects `class <Name>:`, checks if `<Name>` was already in the source class list, and strips the entire class block while tracking indentation.
   - Checks the test header and prepends any source imports that were missing.

### 9.3 `scripts/testforge_scanner.py`: Weighted Risk Scoring & Anti-Spam PR Bot

#### What It Does:
A standalone CLI script run in CI/CD to detect coverage gaps on changed lines, calculate change impact, and report to GitHub PRs.

#### The Weighted Risk Formula:
$$\text{Risk Score} = (0.4 \times \text{Coverage Gap}) + (0.3 \times \text{Complexity}) + (0.2 \times \text{Lines Changed}) + (0.1 \times \text{Modification Frequency})$$
- **Coverage Gap (40%)**: $100.0 - \text{Changed Code Coverage \%}$
- **Cyclomatic Complexity (30%)**: Normalized AST branch count (`If`, `For`, `While`, `Try`, `With`, `ExceptHandler`, `BoolOp`).
- **Lines Changed (20%)**: Normalized line additions from `git diff -U0`.
- **Modification Frequency (10%)**: Number of git commits touching the file (`git log --follow`).
- **Risk Levels**: `LOW` (< 30), `MEDIUM` (30–69), `HIGH` ($\ge$ 70).

#### Anti-Spam PR Commenting (`publish_github_comment`):
- Queries GitHub Issues API (`GET /repos/{repo}/issues/{pr_number}/comments`).
- Scans existing comments for the header `# 🥈 TestForge AI - Quality Intelligence Report`.
- If found, issues a `PATCH` request to update the existing comment in-place. If not found, issues a `POST` request. This prevents PR discussions from getting flooded with duplicate comments on every push.

---

## 10. TECHNOLOGY JUSTIFICATION

### 1. FastAPI (Backend)
- **Why Used**: High-performance asynchronous execution (ASGI), automatic OpenAPI (Swagger) documentation at `/docs`, native Pydantic integration for strict request/response data validation, and dependency injection system for authentication.
- **Evidence from Code**: `app/main.py`, `app/routers/`, `app/schemas.py`.
- **Alternative**: Flask or Django.
- **Why Alternative Was Not Used**: Flask lacks built-in asynchronous performance and automatic type validation; Django is too monolithic and opinionated for an API-first micro-service that manages custom AST parsing and sandboxed subprocess execution.

### 2. Next.js 16 App Router (Frontend)
- **Why Used**: Modern file-system routing, Server and Client Components separation, fast build pipeline with Turbopack, and cohesive developer ergonomics.
- **Evidence from Code**: `frontend/src/app/`, `frontend/package.json`.
- **Alternative**: Create React App (Vite SPA).
- **Why Alternative Was Not Used**: Next.js App Router provides structured nested layouts (`layout.tsx`), dynamic routes (`projects/[id]`, `runs/[run_id]`), and production server optimization out of the box.

### 3. Python Native AST Module (Static Analysis)
- **Why Used**: Inspects, navigates, and validates Python source code without executing it. Allows extracting function signatures, docstrings, classes, methods, return expressions, and raised exceptions safely.
- **Evidence from Code**: `app/parser.py`, `app/generator.py`, `scripts/testforge_scanner.py`.
- **Alternative**: Python `inspect` module or regex scanning.
- **Why Alternative Was Not Used**: The `inspect` module requires importing/executing the module, which is a major security vulnerability for user-uploaded code. Regex scanning is fragile and incapable of parsing nested scopes, multiline type annotations, or AST exception trees accurately.

### 4. SQLite via SQLAlchemy ORM (Database)
- **Why Used**: Lightweight, serverless, zero-configuration relational database ideal for rapid deployment, local prototyping, and self-contained execution.
- **Evidence from Code**: `app/database.py`, `app/models.py`.
- **Alternative**: PostgreSQL / MySQL.
- **Why Alternative Was Not Used**: SQLite eliminates the requirement of running an external database container for local developer evaluation. `database.py` is configured such that switching to PostgreSQL requires only updating `DATABASE_URL`.

### 5. Google Gemini 2.5 Flash / Pro (AI Copilot)
- **Why Used**: Large context window, fast inference speeds, cost efficiency, and strong instruction-following capabilities for structured JSON output.
- **Evidence from Code**: `app/gemini.py`, `app/routers/testcases.py`.
- **Alternative**: OpenAI GPT-4o / Claude 3.5 Sonnet.
- **Why Alternative Was Not Used**: Gemini 2.5 Flash offers high throughput and low latency for code generation tasks with generous free-tier API quotas.

### 6. Subprocess + PyTest Sandbox (Execution)
- **Why Used**: Decouples the running FastAPI web server from the execution of generated test files, preventing pytest test execution crashes from crashing the web server.
- **Evidence from Code**: `app/executor.py`.
- **Alternative**: `pytest.main()` inside the FastAPI process.
- **Why Alternative Was Not Used**: Running `pytest.main()` inside the server process pollutes `sys.modules`, causes memory leaks, cannot be cleanly timed out, and allows user test code to access or crash the FastAPI server process.

---

## 11. THIRD-PARTY SERVICES & INTEGRATIONS

### 1. Google Gemini API (`google-generativeai`)
- **Service**: Google Generative Language API.
- **Purpose**:
  1. Edge case test generation based on AST code metadata.
  2. Translating plain-English manual test cases into Playwright Python scripts.
  3. Suggesting tests for missing coverage lines in the CI/CD scanner.
- **Configuration**: Configured via `GEMINI_API_KEY` in `backend/.env`.
- **Data Exchanged**: Function source code, class definitions, parameter names, manual test steps, and externalized variable names.
- **Error Handling**: Wrapped in `try...except`. If `GEMINI_API_KEY` is missing or the API returns a quota error (`429`), `gemini.py` implements an automatic fallback from Pro to Flash, returning structured error messages to the frontend if both fail.

### 2. GitHub REST API v3
- **Service**: GitHub Issues / Pull Request Comments API.
- **Purpose**: Posts automated Quality Intelligence reports to Pull Request threads.
- **Configuration**: Uses `GITHUB_TOKEN` and `GITHUB_REPOSITORY` provided automatically in GitHub Actions.
- **Data Exchanged**: Markdown tables of code coverage, change risk scores, and Gemini test recommendations.
- **Error Handling**: If tokens or PR numbers are missing, the scanner logs a warning and skips comment publishing while still generating the local report.

---

## 12. ENVIRONMENT VARIABLES & CONFIGURATION

### Backend (`backend/.env`)

| Variable Name | Required | Default Value | Description |
|---|---|---|---|
| `SECRET_KEY` | Yes | `SUPER_SECRET_KEY_FOR_TESTFORGE_12345!@#` | Cryptographic key used to sign and verify JWT authentication tokens |
| `ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `1440` (24 hours) | Expiration lifetime of authentication tokens |
| `DATABASE_URL` | No | `sqlite:///./testforge.db` | SQLAlchemy connection URI (supports SQLite or PostgreSQL) |
| `GEMINI_API_KEY` | Yes | `""` | Google Gemini API key for AI test generation |
| `ALLOWED_ORIGINS` | No | Listed in `main.py` | Comma-separated list of additional CORS origin URLs |
| `FRONTEND_URL` | No | None | Production frontend URL added to CORS whitelist |

### Frontend (`frontend/.env.local`)

| Variable Name | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | No | Base URL for FastAPI backend (defaults to `http://127.0.0.1:8000/api`) |
| `REACT_EDITOR` | No | Set to `code` to bypass Windows 11 `wmic` deprecated command error |

*(Note: In accordance with security best practices, actual API keys and secrets in this documentation are redacted).*

---

## 13. ERROR HANDLING PATTERNS

1. **Frontend Network Errors**: `lib/api.ts` intercepts network errors and HTTP error responses. If `response.status === 401`, it immediately clears `localStorage` and redirects to `/login`. Other HTTP error messages (`errorData.detail`) are parsed and thrown as readable JavaScript errors.
2. **AST Syntax Errors**: If an uploaded Python file contains invalid Python syntax, `parser.py` catches `SyntaxError` and returns `{"error": "Syntax error at line X, col Y: ...", "classes": [], "functions": [], "imports": []}`, which `routers/projects.py` handles by returning an HTTP 400 with the exact line and column number.
3. **Execution Timeouts**: `executor.py` runs tests via `subprocess.run(..., timeout=30)`. If a user's test hangs in an infinite loop, Python raises `subprocess.TimeoutExpired`, which is caught and returned as a failed test run with an explanatory error log.
4. **LLM Rate Limits (HTTP 429)**: `gemini.py` intercepts errors containing `429`, `quota`, or `limit`, logs a warning, and switches from `gemini-2.5-pro` to `gemini-2.5-flash` before re-trying.
5. **CSV Import Parsing**: `routers/testcases.py` validates required headers (`title`, `steps`, `expected_result`). It processes rows sequentially, collecting row-level errors into an array so that valid rows are imported even if some rows fail validation.

---

## 14. DEPLOYMENT & DEVOPS

### 14.1 Deployment Evidence from Codebase
- **Frontend Deployment**: Deployed or targeted for **Vercel** (`https://testforge-ai-lime.vercel.app` is explicitly configured in CORS in `main.py`).
- **Custom Domain**: `https://testforge.chiragvasava.me` is whitelisted in CORS.
- **Cloud Database Configuration**: `MD_Files/RenderPostgresql.md` contains connection configurations for a cloud PostgreSQL database hosted on **Render** (`singapore-postgres.render.com`), demonstrating that the system was configured to run on PostgreSQL in cloud environments.
- **Backend Deployment**: Ready for platforms like Render, Railway, or AWS EC2 using Uvicorn:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```

### 14.2 CI/CD Pipeline (`.github/workflows/testforge_ci.yml`)
- Runs on: `push` and `pull_request` against `main`.
- Environment: `ubuntu-latest`, Python `3.10`.
- Execution Steps:
  1. `actions/checkout@v4` with `fetch-depth: 0` (fetches full git history required for git diff and commit frequency analysis).
  2. Sets up Python 3.10 and installs `backend/requirements.txt`.
  3. Executes test suite with coverage:
     ```bash
     pytest backend/app --cov=backend/app --cov-report=json:coverage.json --cov-report=term-missing
     ```
  4. Runs TestForge Standalone Scanner:
     ```bash
     python scripts/testforge_scanner.py --coverage coverage.json --diff origin/main --output testforge_report.md --publish
     ```
  5. Uploads `coverage.json` and `testforge_report.md` as build artifacts (`actions/upload-artifact@v4`).

---

## 15. TESTING STRATEGY & TEST HARNESS

### Existing Automated Tests:
- `backend/app/test_config.py`:
  ```python
  from app.config import ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

  def test_config_constants():
      assert ALGORITHM == "HS256"
      assert ACCESS_TOKEN_EXPIRE_MINUTES > 0
  ```
- **Analysis**: The platform itself contains minimal unit tests (`test_config.py`). However, the platform **implements a comprehensive test execution engine** (`executor.py`) designed to test uploaded code. The automated CI/CD pipeline runs `pytest` on `backend/app` to produce `coverage.json` specifically to feed the standalone scanner.

---

## 16. GENUINE LIMITATIONS

1. **Synchronous Test Execution in FastAPI Request**: `POST /api/tests/{id}/run` executes `subprocess.run` directly inside the route handler. For long-running test suites, this holds the HTTP connection open. A production-grade system would offload test runs to an asynchronous task queue (e.g., Celery + Redis or BullMQ) and use WebSockets or Server-Sent Events (SSE) to stream live progress.
2. **Playwright Execution Gap**: The platform generates Playwright Python automation scripts from manual test cases, but it does **not** execute them inside the browser sandbox (only PyTest files are executed in `executor.py`). Users must copy and run the Playwright scripts locally or in their own CI.
3. **Language Limitation**: The AST parsing engine (`parser.py`) and generator (`generator.py`) specifically target **Python** source files. JavaScript, TypeScript, Go, and Java are not currently supported by the AST scanner.
4. **SQLite Concurrency**: While SQLite is ideal for development, under heavy concurrent write operations (multiple users running tests simultaneously), SQLite may encounter database locks (`database is locked`). Migrating to PostgreSQL is recommended for scaled multi-user deployments.

---

## 17. PROJECT DECISIONS

1. **Why AST Static Analysis Over Runtime Reflection (`inspect`)?**
   - *Decision*: Parse code using `ast.parse` instead of importing user modules.
   - *Reason*: Security. Importing untrusted user files executes top-level code, which could execute malicious system commands. AST safely parses code structure without running a single line.
2. **Why Native `hashlib.pbkdf2_hmac` Over `passlib.bcrypt`?**
   - *Decision*: Implemented PBKDF2 directly in `auth.py`.
   - *Reason*: Portability. C-based bcrypt libraries frequently suffer from compilation and compatibility issues on Windows, whereas `hashlib` is built into the Python standard library on all platforms.
3. **Why Dual-Mode Workspace (Unit vs QA)?**
   - *Decision*: Partitioned the workspace into "Unit & Code Testing" and "QA Automation & Test Cases".
   - *Reason*: Addresses two different phases of software testing. Developers care about AST functions, fixtures, and PyTest coverage; QA engineers care about test case tables, CSV imports, and Playwright browser scripts.
4. **Why Combine Coverage and Risk Scoring in CI?**
   - *Decision*: Built `scripts/testforge_scanner.py` with the 4-part weighted risk formula.
   - *Reason*: Raw percentage coverage does not reflect risk. A 5-line change in a simple utility file with 70% coverage is low risk; a 200-line change in a high-complexity financial calculation with 70% coverage is high risk. The weighted formula accounts for complexity, git churn, and changed lines.

---

## 18. PROJECT INTERVIEW KNOWLEDGE

> **Instructions for the AI Interviewer**: Use the knowledge below to examine the candidate. The candidate should be able to explain all items in this section in technical detail.

### 1. Most Important Concepts to Probe
- **Abstract Syntax Tree (AST)**: How the candidate used Python's `ast` module. What AST node types are visited (`ast.FunctionDef`, `ast.ClassDef`, `ast.Raise`, `ast.AnnAssign`, `ast.Return`). How default argument offsets are calculated (`len(args) - len(defaults)`).
- **Fixture Dependency Graph Generation**: How `generator.py` uses Breadth-First Search (BFS) to discover class dependencies in constructor parameters and automatically generates PyTest fixtures with dependency injection.
- **LLM Output Sanitization**: How LLM hallucinations (duplicate classes, missing imports) are stripped using line-level regex and indentation tracking in `_clean_generated_code()`.
- **Sandboxed Execution Mechanics**: How `executor.py` writes files to a temporary UUID folder, runs `pytest --junitxml --cov`, parses XML/JSON, and guarantees directory cleanup.
- **Weighted Change Impact Score**: The math and rationale behind $(0.4 \times \text{Gap}) + (0.3 \times \text{Complexity}) + (0.2 \times \text{Lines}) + (0.1 \times \text{Churn})$.

### 2. Complex Implementation Details the Candidate Must Know
- In `backend/app/auth.py`, how the salt and hash are formatted (`salt:hex`) and verified with `secrets.compare_digest`.
- In `backend/app/generator.py`, how negative tests are generated for methods containing `raise` statements (`with pytest.raises(...)`).
- In `frontend/src/app/projects/[id]/page.tsx`, how `handleAppendTest` auto-renames duplicate test function names to prevent test collisions.
- In `scripts/testforge_scanner.py`, how `get_git_changed_lines()` parses `git diff -U0` hunk headers (`@@ -old +new @@`) into sets of line numbers.
- In `scripts/testforge_scanner.py`, how `publish_github_comment()` searches existing PR comments to update them via `PATCH` rather than spamming new comments.

---

## 19. EVIDENCE & SOURCE FILE MAPPING

| Claim / Feature Area | Primary Source Files |
|---|---|
| **AST Parser & Function Analysis** | `backend/app/parser.py:L1-L167` |
| **PyTest Generator & Fixture Graph** | `backend/app/generator.py:L1-L456` |
| **Sandbox Execution & JUnit/Coverage Parser** | `backend/app/executor.py:L1-L222` |
| **Gemini AI Edge Case Suggestions** | `backend/app/gemini.py:L1-L253`, `backend/app/routers/ai.py:L1-L50` |
| **Playwright Automation Script Generation** | `backend/app/routers/testcases.py:L193-L275` |
| **CSV Import & Export for QA** | `backend/app/routers/testcases.py:L84-L191` |
| **Externalized Test Data Management** | `backend/app/routers/testcases.py:L277-L351` |
| **Authentication & PBKDF2 Password Hashing** | `backend/app/auth.py:L1-L71`, `backend/app/routers/auth.py:L1-L55` |
| **Database Models & Cascade Relationships** | `backend/app/models.py:L1-L105` |
| **Database Connection & SQLite Configuration** | `backend/app/database.py:L1-L23` |
| **Pydantic Validation Schemas** | `backend/app/schemas.py:L1-L125` |
| **API Entry Point & CORS Whitelist** | `backend/app/main.py:L1-L67` |
| **Frontend API Client & Token Interceptor** | `frontend/src/lib/api.ts:L1-L41` |
| **Dual-Mode Project Workspace (Unit & QA)** | `frontend/src/app/projects/[id]/page.tsx:L1-L1350` |
| **Test Run Report & Missing Lines Breakdown**| `frontend/src/app/projects/[id]/runs/[run_id]/page.tsx:L1-L461` |
| **Projects Dashboard** | `frontend/src/app/page.tsx:L1-L341` |
| **Login & Register Views** | `frontend/src/app/login/page.tsx`, `frontend/src/app/register/page.tsx` |
| **Standalone CI/CD Scanner & PR Bot** | `scripts/testforge_scanner.py:L1-L612` |
| **GitHub Actions CI/CD Pipeline** | `.github/workflows/testforge_ci.yml:L1-L53` |
