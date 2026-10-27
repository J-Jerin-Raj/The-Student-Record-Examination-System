# Acadence - Dependencies & Modules Specification

## 1. Zero-Dependency Architectural Principle

The entire core application—including the full-stack REST API server ([`app.py`](file:///c:/Users/jebas/projects/The-Student-Record-Examination-System/app.py)), interactive command-line interface ([`main.py`](file:///c:/Users/jebas/projects/The-Student-Record-Examination-System/main.py)), relational SQLite database layer ([`database/`](file:///c:/Users/jebas/projects/The-Student-Record-Examination-System/database)), custom data structures, and automated unit test suite ([`tests/`](file:///c:/Users/jebas/projects/The-Student-Record-Examination-System/tests))—is built **strictly with the Python Standard Library**.

### Key Advantages:
1. **Instant Portability**: Clones and runs immediately on Windows, macOS, or Linux without executing `pip install` or encountering dependency resolution conflicts.
2. **Evaluator Reliability**: University evaluators and automated test runners do not need internet access or package manager configurations.
3. **Low Footprint & High Security**: Zero third-party supply chain vulnerabilities (no vulnerable transitive packages).

---

## 2. Standard Library Modules Catalog

| Python Standard Module | Core Components Used | Implementation Location | Technical Purpose & Justification |
| :--- | :--- | :--- | :--- |
| **`http.server`** | `HTTPServer`, `BaseHTTPRequestHandler` | `app.py` | Implements the lightweight REST API and static asset delivery server on port 8080 without external web frameworks (e.g. Flask, FastAPI). |
| **`sqlite3`** | `connect()`, `Row`, `Cursor` | `database/` | Embedded ACID-compliant SQL persistence. `sqlite3.Row` provides dict-accessible rows for clean dataclass hydration. |
| **`dataclasses`** | `@dataclass`, `field`, `asdict` | `models/`, `algorithms/`, `services/` | Strongly-typed domain representations (`Task`, `Exam`, `Assessment`, `UndoAction`) with automatic `__repr__`, equality, and serializing helpers. |
| **`datetime`** | `datetime`, `timedelta`, `time` | `services/`, `database/seed.py` | Time interval arithmetic for exam conflict checks, live exam countdowns, relative demo seeding, and deadline urgency calculations. |
| **`urllib.parse`** | `urlparse`, `parse_qs` | `app.py` | Parses URL routing paths and extracts query string parameters (e.g. `?hours=3.5`, `?status=Pending`). |
| **`json`** | `dumps()`, `loads()` | `app.py` | Serializes model instances to JSON response bodies and parses incoming client payloads. |
| **`time`** | `perf_counter()` | `algorithms/`, `services/dsa_lab.py` | High-precision wall-clock timer providing fractional-millisecond resolution for empirical Big-O benchmarking. |
| **`random`** | `Random(seed=42)` | `services/dsa_lab.py` | Generates deterministic, reproducible synthetic arrays for benchmarking search and sort performance. |
| **`os` / `sys`** | `path`, `exit`, `argv` | Throughout Project | Resolves operating-system agnostic file paths (`os.path.join`) and handles process lifecycle commands. |
| **`typing`** | `Any`, `Dict`, `List`, `Optional`, `Tuple`, `Callable` | Throughout Project | Type annotations enforcing clean API signatures, static analysis support, and code readability. |
| **`unittest`** | `TestCase`, `assertRaises` | `tests/test_acadence.py` | Automated testing framework executing 9 test suites across all data structures, engines, and services. |

---

## 3. Optional Visualization Dependencies (`requirements.txt`)

For students who wish to run the alternative rich analytical frontend ([`streamlit_app.py`](file:///c:/Users/jebas/projects/The-Student-Record-Examination-System/streamlit_app.py)), optional packages are specified:

```text
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
```

### Purpose of Optional Packages:
* **`streamlit`**: Provides a reactive Python-driven GUI with sidebar navigation, metric cards, and reactive form components.
* **`pandas`**: Formats database query lists into DataFrame tables for tabular presentation and CSV export.
* **`plotly`**: Renders dynamic SVG/WebGL visualizations, including the Crisis Index gauge and revision priority radar charts.

> **Note**: The primary application ([`app.py`](file:///c:/Users/jebas/projects/The-Student-Record-Examination-System/app.py)) and CLI ([`main.py`](file:///c:/Users/jebas/projects/The-Student-Record-Examination-System/main.py)) **do not** require these packages and function completely without them.

---

## 4. Environment & Python Version Matrix

| Python Version | Core Web Server (`app.py`) | Interactive CLI (`main.py`) | Automated Tests (`tests/`) | Streamlit (`streamlit_app.py`) |
| :---: | :---: | :---: | :---: | :---: |
| **Python 3.9** | Supported | Supported | Supported | Supported |
| **Python 3.10** | Supported | Supported | Supported | Supported |
| **Python 3.11** | Fully Tested | Fully Tested | Fully Tested | Supported |
| **Python 3.12** | Supported | Supported | Supported | Supported |
| **Python 3.13** | Supported | Supported | Supported | Supported |
