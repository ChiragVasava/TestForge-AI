# TestForge AI - Technical Audit & Resume Review Report

This report documents every technology, framework, library, tool, platform, API, database, protocol, architecture pattern, testing tool, DevOps tool, cloud service, authentication mechanism, design pattern, and integration used in the TestForge AI project workspace.

---

## 1. Programming Languages
* **TypeScript** (Advanced): Utilized for writing the entire frontend Next.js application, including route handlers, interface components, and API client wrappers with strict typing checks.
* **Python 3** (Expert): Used to build the entire backend REST API, AST parsing engines, test runner sandboxes, CLI utility scanners, and AI integration services.
* **HTML5 / CSS3** (Intermediate): Used for frontend element structures and utility layouts.

---

## 2. Frontend
* **Frameworks**: 
  * **Next.js 16.2.6** (React 19 Server/Client Framework): Powers the frontend with dynamic page rendering (`/projects/[id]`), client-side layouts, page optimization, and webpack/Turbopack configurations.
* **Libraries**:
  * **React 19.2.4**: Used to build modular hooks, states, and client-side page views.
  * **React-DOM 19.2.4**: Core virtual DOM mapper for Next.js.
* **UI Frameworks**:
  * **TailwindCSS v4**: Configured with PostCSS, providing utility class layouts, interactive dark themes, hover transitions, and clean layout grids.
* **State Management**:
  * **React Context & State Hooks** (`useState`, `useEffect`): Handles active tabs, upload loading states, selected codes, project details, and execution logs.
* **Routing**:
  * **Next.js App Router** (File-system based dynamic routing): Utilized to load project details under `/projects/[id]` and test runs at `/projects/[id]/runs/[run_id]`.
* **Forms**:
  * **HTML5 native forms / inputs**: Managed using React states for registration, login, and sidebar files selection.
* **Validation**:
  * **TypeScript types / client-side validations**: Enforces parameter requirements on forms and API payloads before network delivery.
* **Charts**:
  * **Recharts v3.8.1**: Used to render SVG charts plotting coverage changes, code stability, and complexity distributions over time.
* **Editors**:
  * **Read-only textareas / pre blocks**: Used to present read-only generated PyTest suites, Gemini recommendations, and standard console outputs.
* **Utilities**:
  * **Lucide React v1.17.0**: Providing premium vector icons (folder, upload, run, test suite, coverage dashboard, locks).
  * **Custom API Client Wrapper** (`lib/api.ts`): Extends `fetch` to automatically append JWT bearer headers, manage session logouts on 401s, and handle payload serialization.

---

## 3. Backend
* **Frameworks**:
  * **FastAPI**: Main ASGI backend API framework handling routers, body validation dependencies, path parameters, and JSON serialization.
* **Authentication**:
  * **OAuth2 (Password Bearer Flow)**: Managed via FastAPI's `OAuth2PasswordBearer` and `OAuth2PasswordRequestForm` injection.
  * **python-jose [cryptography]**: Used for encoding, signing, and decoding JWT (JSON Web Tokens) access sessions.
* **Authorization**:
  * **Dependency Injection Access Restrictions**: REST endpoints verify project database ownership (`project.owner_id == current_user.id`) before allowing uploads, recommendations, or test runs.
* **Validation**:
  * **Pydantic**: Validates REST request bodies and enforces strict response type schemas (defined in `app/schemas.py`).
  * **email-validator**: Integrated with Pydantic schemas to validate user email formats during registration/login.
* **ORM**:
  * **SQLAlchemy**: Relational mapper defining class schemas (`User`, `Project`, `ProjectFile`, `GeneratedTest`, `TestRun`, `TestCase`) and handling session transactions.
* **File Upload**:
  * **python-multipart**: Parses incoming `multipart/form-data` uploads (e.g. `decorators.py`, `models.py`) from the frontend clients.
* **Background Jobs**:
  * **Python Subprocess Orchestration**: Local test executions are run asynchronously as sandbox processes.
* **Logging**:
  * **Python Logging Engine**: Handles uvicorn standard API status prints.
* **Middleware**:
  * **FastAPI CORSMiddleware**: Handles cross-origin requests, configured to allow local frontend ports (`3000`, `3001`, `3002`) and your production Vercel frontend.
* **API Framework**:
  * **Uvicorn**: High-performance ASGI web server hosting the FastAPI application.

---

## 4. Database
* **Databases**:
  * **SQLite**: Lightweight file-based SQL database engine configured for local workspace development.
* **ORMs**:
  * **SQLAlchemy Core & Declarative Mapper**: Maps models to SQL tables and handles transactions (`db.commit()`, `db.refresh()`).
* **Migration Tools**:
  * **SQLAlchemy Declarative Base Metadata**: Runs `Base.metadata.create_all(bind=engine)` at application startup to automatically build tables if they do not exist.
* **Database Drivers**:
  * **sqlite3**: Built-in Python sqlite driver.

---

## 5. AI
* **LLMs**:
  * **Gemini 2.5 Pro** / **Gemini 2.5 Flash**: Orchestrated to analyze source files, suggest parameterized edge cases, and build assertions.
* **AI SDKs**:
  * **google-generativeai**: The official Google AI Python SDK for interacting with Gemini models.
* **Embedding**:
  * None.
* **Prompt Engineering**:
  * **System Instructions / AST-Context Prompts**: Constructs structured context prompts by feeding the parsed AST structure (classes, methods, fields) directly into the prompt context to enforce quality output.
* **Vector DB**:
  * None.
* **Inference APIs**:
  * **Google Generative AI API**: Accesses Gemini endpoints securely using a `GEMINI_API_KEY`.

---

## 6. Testing
* **Unit Testing**:
  * **pytest**: Runs unit tests for configuration structures.
* **Integration Testing**:
  * **Subprocess execution tests**: Integrates CLI pipelines with coverage analyzers.
* **E2E Testing**:
  * **CI Pipeline Integration Run**: Executes the local scanner end-to-end to verify report generation.
* **API Testing**:
  * **Automated Python Verification Client** (`scratch/local_verify.py`): Performs authentication, parses files, recommends tests, adds duplicate code mocks, and saves and runs test suites to assert coverage.
* **Coverage**:
  * **pytest-cov**: Measures statement execution coverage, outputting JSON logs (`coverage.json`).

---

## 7. DevOps
* **Docker**:
  * None.
* **GitHub Actions**:
  * **testforge_ci.yml**: CI pipeline running on every commit/PR, installing dependencies, executing tests, running the scanner script, and uploading coverage reports.
* **CI/CD**:
  * **Automated Scanner Action Pipeline** (`scripts/testforge_scanner.py`): Integrates with GitHub Actions to calculate risk, generate markdown reports, and comment directly on PR pages.
* **Build Tools**:
  * **Next.js Builder (Turbo/Webpack)**: Optimizes assets and type-checks during builds.
  * **pip**: Python package manager.
* **Deployment**:
  * **Vercel**: Hosts the Next.js frontend with serverless routes.

---

## 8. Cloud
* **AWS**:
  * None.
* **Vercel**:
  * **Next.js hosting platform**: Connects directly to the GitHub repository to run builds on commit.
* **Render / Railway / Firebase / Appwrite / Supabase**:
  * None (local SQLite and Uvicorn server are used for backend database and API execution).

---

## 9. APIs & Integrations
* **Payment**:
  * None.
* **Email**:
  * None.
* **Authentication**:
  * **Local JWT auth system**: Issue and validation of session tokens.
* **Third-party APIs**:
  * **GitHub PR Comments API**: Updates discussion comments on pull requests.
  * **Google Generative AI API**: Generates unit test edge cases.

---

## 10. Security
* **JWT**: Sessions are signed using cryptographic signatures via `python-jose`.
* **bcrypt**: Securely hashes database passwords before saving.
* **OAuth**: Utilized for standard FastAPI token authentication.
* **CORS**: Restricts domain requests, explicitly allowing your Vercel client.
* **Rate Limiting**: Handles rate limits on the Gemini API with a fallback algorithm that automatically falls back to Gemini Flash if a 429 status is returned.
* **Helmet / CSRF / Validation**: Enforces standard browser CORS rules, and validates inputs via Pydantic on the backend and TypeScript types on the frontend.

---

## 11. Architecture
* **REST**: RESTful endpoints communicate via JSON over HTTP.
* **Monolith / Monorepo**: The project is structured as a monorepo containing `/frontend` and `/backend` components.
* **AST (Abstract Syntax Tree) Parser Engine**: Reads source files using Python's standard `ast` package to build complexity maps and dependency graphs.
* **Topological Fixture Dependency Graph Resolver**: Analyzes constructor arguments and classes recursively to inject matching fixtures.
* **Sandbox PyTest Executor**: Sandboxes file creation in temporary directories, running pytest subprocesses safely.

---

## 12. Other Technologies
* **re (Regular Expressions)**: Parses mock parameters, strips duplicate imports, and renames duplicate functions during appends.
* **urllib.request**: Standard library request calls posting CI updates to GitHub without external dependencies.
* **git**: Scans diff states (`git diff`), commit histories (`git log`), and handles repository pushes.

---

## 13. Resume Recommendation

### A. Technologies to Definitely Include (Real Hands-on Experience)
* **Python, TypeScript, React, Next.js, FastAPI** (Core stack)
* **SQLAlchemy ORM, SQLite** (Data layer)
* **AST (Abstract Syntax Trees) & AST Parsing** (A major differentiator: highlight building the dependency graph resolver)
* **Subprocess Sandboxing** (Highlights building safe execution test runners)
* **CORS Middleware & JWT Bearer Authentication** (Backend security fundamentals)
* **TailwindCSS** (Modern layout design)

### B. Technologies to Mention Only If You Understand Well
* **GitHub API / Webhooks Integration** (PR commenter)
* **Gemini Generative AI API SDK** (Used for test suggestions)
* **Git CLI / Diff Engines** (Used to check changed line code complexity)

### C. Technologies to NOT Include (Config-only or Auto-generated)
* **Uvicorn / Webpack / PostCSS / ESLint** (These are dev tooling/configs; list them only if explicitly requested, but keep focus on Next.js/FastAPI)
* **python-dotenv / python-multipart** (Libraries that support features; describe the *feature* instead: "File upload parsers" and "Environment managers")

### D. Technologies Recruiters Expect You to Know
* **Git, GitHub, GitHub Actions (CI/CD)**
* **Unit Testing (pytest)**
* **REST APIs / JSON Serialization**
* **SQL Database Schemas**

---

## 14. Confidence Rating
* **Python**: `Expert` (Core of AST parsing, AST generators, subprocess runners, and CLI scanning)
* **FastAPI**: `Advanced` (Custom routing, OAuth dependency injection, CORSMiddleware)
* **SQLAlchemy**: `Advanced` (Complex relationships, database connection managers)
* **TypeScript & Next.js**: `Advanced` (Type-checked dynamic page views, localStorage auth client hooks)
* **pytest**: `Advanced` (Assertion templates, parameterized fixtures, coverage JSON reports)
* **TailwindCSS**: `Advanced` (Dark mode layouts, flex/grid layouts)
* **Google Generative AI SDK**: `Advanced` (Engineered fallbacks, system instructions, AST prompts)
* **GitHub Actions**: `Advanced` (Pipeline automation, upload artifacts, setup runners)
* **SQLite**: `Intermediate` (Configured local relational mappings)
* **GitHub API / urllib**: `Intermediate` (PR comment posts)
* **Vercel**: `Configuration Only` (Linked repository deployment host)
