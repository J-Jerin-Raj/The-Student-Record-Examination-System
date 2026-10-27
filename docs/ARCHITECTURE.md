# Acadence - System Architecture & Technical Design

## 1. System Overview & Philosophy

**Acadence** is a multi-tier academic productivity, schedule conflict detection, and examination planning system. It is designed to demonstrate computer science and Data Structures & Algorithms (DSA) coursework concepts—specifically **CO1** (Linear Data Structures: Stack & Queue), **CO2** (Linked Lists & Sequential Search), and **CO3** (Divide-and-Conquer Algorithms & Asymptotic Complexity Analysis)—while delivering a zero-external-dependency, production-grade application.

The core architecture follows a **Decoupled 4-Tier Layered Design** ensuring that domain data structures, business logic, persistence, and presentation interfaces remain strictly separated.

---

## 2. Layered Architecture Diagram

```mermaid
flowchart TD
    subgraph PresentationLayer["1. Presentation & Interface Layer"]
        UI_SPA["Web SPA Dashboard<br/>(HTML5 / CSS3 / Vanilla JS)"]
        UI_CLI["Interactive ANSI CLI<br/>(main.py)"]
        UI_ST["Streamlit Analytics UI<br/>(streamlit_app.py)"]
    end

    subgraph TransportLayer["2. Transport & Controller Layer (app.py)"]
        HTTP_SRV["Zero-Dependency HTTP Server<br/>(http.server.HTTPServer)"]
        ROUTER["RESTful Dispatcher<br/>(do_GET, do_POST, do_PUT, do_DELETE)"]
        STATIC_HDL["Static Asset Resolver<br/>(/static/css, /static/js)"]
    end

    subgraph ServiceLayer["3. Domain Services & Business Logic"]
        SRV_PLANNER["AcademicPlannerService<br/>(Undo Engine, Study Scheduler)"]
        SRV_EXAM["ExamManagerService<br/>(Clash Detection, Countdown)"]
        SRV_PERF["PerformanceAnalyzerService<br/>(Averages, Decline Alerts, Target Calc)"]
        SRV_RESCUE["AcademicRescueService<br/>(Triage Engine, Crisis Index)"]
        SRV_PRIORITY["PriorityEngine<br/>(Multi-Factor Scoring Matrix)"]
        SRV_LAB["DSALabService<br/>(Empirical Benchmark Trials)"]
    end

    subgraph DSALayer["4. Core Data Structures & Algorithms (CO1, CO2, CO3)"]
        DS_STACK["LIFO Stack<br/>(data_structures/stack.py)"]
        DS_QUEUE["FIFO Linked Queue<br/>(data_structures/queue.py)"]
        DS_LL["Singly Linked List<br/>(data_structures/linked_list.py)"]
        ALGO_SORT["Sorting Suite<br/>(Bubble, Insertion, Merge Sort)"]
        ALGO_SEARCH["Searching Suite<br/>(Linear, Binary Search)"]
        MODELS["Domain Models<br/>(Task, Exam, Assessment, Request, Action)"]
    end

    subgraph PersistenceLayer["5. Persistence & Storage Layer"]
        DB_FACADE["Database Facade<br/>(database/__init__.py)"]
        DB_OPS["CRUD Operations<br/>(database/operations.py)"]
        DB_SCHEMA["Schema & Seeding<br/>(schema.py & seed.py)"]
        SQLITE_FILE[("SQLite File<br/>acadence.db")]
    end

    %% Presentation to Transport
    UI_SPA -->|HTTP REST JSON| ROUTER
    STATIC_HDL -->|CSS / JS / HTML| UI_SPA
    HTTP_SRV --> ROUTER

    %% CLI and Streamlit direct access
    UI_CLI --> ServiceLayer
    UI_ST --> ServiceLayer

    %% Router to Services
    ROUTER --> SRV_PLANNER
    ROUTER --> SRV_EXAM
    ROUTER --> SRV_PERF
    ROUTER --> SRV_RESCUE
    ROUTER --> SRV_PRIORITY
    ROUTER --> SRV_LAB

    %% Services to DSA Core
    SRV_PLANNER --> DS_STACK
    SRV_PLANNER --> DS_LL
    SRV_PLANNER --> SRV_PRIORITY
    SRV_EXAM --> DS_QUEUE
    SRV_EXAM --> ALGO_SORT
    SRV_EXAM --> ALGO_SEARCH
    SRV_LAB --> ALGO_SORT
    SRV_LAB --> ALGO_SEARCH
    SRV_LAB --> DS_LL
    SRV_RESCUE --> SRV_PRIORITY
    SRV_RESCUE --> SRV_PERF

    %% Data Models cross-cutting
    MODELS -.-> ServiceLayer
    MODELS -.-> DSALayer
    MODELS -.-> PersistenceLayer

    %% Services to Persistence
    SRV_PLANNER --> DB_FACADE
    SRV_EXAM --> DB_FACADE
    SRV_PERF --> DB_FACADE
    SRV_RESCUE --> DB_FACADE
    DB_FACADE --> DB_OPS
    DB_FACADE --> DB_SCHEMA
    DB_OPS --> SQLITE_FILE
    DB_SCHEMA --> SQLITE_FILE
```

---

## 3. Tier-by-Tier Architectural Breakdown

### Tier 1: Presentation & User Interfaces
Acadence provides three concurrent, non-conflicting user interfaces:
1. **Single-Page Application (SPA)**: Handcrafted with semantic HTML5, pure CSS custom properties (`--bg`, `--surface`, `--primary`), and vanilla JavaScript (`static/js/app.js`). Zero frontend framework dependencies (`React`, `Vue`, `Tailwind` not required).
2. **Interactive Terminal CLI (`main.py`)**: Designed for headless servers, examiners, and terminal power-users. Features ANSI color escapes (`\033[96m`), ASCII tabular alignment, and guided workflow menus.
3. **Streamlit Analytics Dashboard (`streamlit_app.py`)**: Optional visualization layer using Streamlit and Plotly for graphical grade trend curves and interactive radar charts.

### Tier 2: Transport & API Routing (`app.py`)
* Built directly on Python standard library `http.server.HTTPServer` and `BaseHTTPRequestHandler`.
* Manages HTTP lifecycle:
  * Static file delivery with MIME-type resolution (`text/html`, `text/css`, `application/javascript`).
  * REST API routing with method dispatching (`do_GET`, `do_POST`, `do_PUT`, `do_DELETE`).
  * Cross-Origin Resource Sharing (CORS) headers and JSON serialization.

### Tier 3: Application Services (`services/`)
Encapsulates all domain business logic and algorithmic orchestration:
* **`PriorityEngine`**: Evaluates task urgency, user priority, academic subject vulnerability, and estimated effort to output explainable priority scores.
* **`AcademicRescueService`**: Calculates the systemic academic **Crisis Index** (0 to 100) and curates emergency triage recommendations.
* **`AcademicPlannerService`**: Bridges persistent SQLite storage with the in-memory **LIFO Stack** to provide instant $\mathcal{O}(1)$ rollback for modifications.
* **`ExamManagerService`**: Orchestrates examination schedules, pairwise interval clash detection ($\mathcal{O}(n^2)$), and the **FIFO Service Queue**.
* **`PerformanceAnalyzerService`**: Computes weighted cumulative grade averages, multi-assessment trajectory trends, decline detection, and target exam mark reverse-engineering.
* **`DSALabService`**: Executes controlled empirical benchmarking on searching, sorting, and storage data structures across datasets up to $N = 5,000$.

### Tier 4: Core Data Structures & Algorithms (`data_structures/`, `algorithms/`)
Hand-crafted fundamental computer science structures implemented from first principles:
* **Custom Node (`Node`)**: Data reference and dynamic pointer chaining.
* **Singly Linked List (`SinglyLinkedList`)**: Dynamic node allocation with $\mathcal{O}(1)$ head insertion and sequential traversal.
* **LIFO Stack (`Stack`)**: Dynamic array-backed stack with capacity boundaries, enforcing strict Last-In, First-Out order.
* **FIFO Queue (`Queue`)**: Linked-node queue with dedicated `_front` and `_rear` pointers guaranteeing strict $\mathcal{O}(1)$ enqueue and dequeue operations without array shift penalties.
* **Sorting Algorithms**: Bubble Sort with early termination flag, Insertion Sort with shift counting, and recursive Merge Sort.
* **Searching Algorithms**: Sequential Linear Search on linked lists and arrays, and Divide-and-Conquer Binary Search on sorted lists.

### Tier 5: Persistence Layer (`database/`)
* **Engine**: SQLite 3 (embedded in Python standard library).
* **Connection Manager (`connection.py`)**: Configures `sqlite3.Row` factory for dictionary-like column access and maintains thread-safe file paths.
* **Schema Definition (`schema.py`)**: DDL table definitions and clean data wipe procedures.
* **Seeding Engine (`seed.py`)**: Generates realistic academic records using relative timestamps (`now + timedelta(days=X)`) so demo data is consistently active.
* **Operations Layer (`operations.py`)**: Parameterized SQL queries preventing SQL injection vulnerabilities.

---

## 4. Architectural Design Patterns

| Pattern | Component | Implementation Detail |
| :--- | :--- | :--- |
| **Memento / Command** | Multi-Level Undo Engine | When a task is created, updated, or deleted, an `UndoAction` snapshot containing the previous and new states is pushed onto the `Stack`. Reverting pops the token and executes the inverse database operation. |
| **Facade Pattern** | `database/__init__.py` | Shields all services and API routes from low-level SQLite cursor mechanics, SQL queries, and connection lifecycles by exposing clean top-level functions. |
| **Strategy Pattern** | `algorithms/sorting.py` | Encapsulates multiple sorting algorithms (`bubble`, `insertion`, `merge`) behind interchangeable callable interfaces accepting common parameters (`arr`, `key_func`, `reverse`). |
| **Triage Pattern** | `AcademicRescueService` | Evaluates multi-dimensional risk signals (overdue tasks, impending deadlines, grade vulnerabilities) into a unified priority queue of actionable recommendations. |
| **Zero-Dependency Pattern** | Entire Core System | Core server, database, models, algorithms, and CLI execute purely on standard library Python, eliminating `node_modules`, `pip` dependencies, or environment conflicts during evaluation. |

---

## 5. End-to-End Sequence Diagram (Example: Task Creation & Undo)

```mermaid
sequenceDiagram
    autonumber
    actor User as Student / Evaluator
    participant UI as Web Dashboard / CLI
    participant API as REST API (app.py)
    participant Planner as AcademicPlannerService
    participant Stack as LIFO Undo Stack
    participant DB as Database Layer (SQLite)

    Note over User,DB: Phase 1: Task Creation
    User->>UI: Submit "Add Task" Form
    UI->>API: POST /api/tasks {title, subject, deadline, effort, priority}
    API->>Planner: add_task(task, push_undo=True)
    Planner->>DB: insert_task(task)
    DB-->>Planner: Return new_task_id = 42
    Planner->>Stack: push(UndoAction(type="CREATE", entity_id=42, previous_state=None))
    Planner-->>API: (success=True, "Task created", id=42)
    API-->>UI: 201 Created {success: true, id: 42}
    UI-->>User: Display Task in Dashboard & Enable "Undo" Button

    Note over User,DB: Phase 2: Undo Execution
    User->>UI: Click "Undo Last Action" Button
    UI->>API: POST /api/undo
    API->>Planner: undo_last_action()
    Planner->>Stack: pop()
    Stack-->>Planner: Returns UndoAction(type="CREATE", entity_id=42)
    Planner->>DB: delete_task(42)
    DB-->>Planner: Confirmation (rowcount > 0)
    Planner-->>API: (success=True, "Reverted Task #42 creation")
    API-->>UI: 200 OK {success: true, message: "Reverted..."}
    UI-->>User: Remove Task from View & Toast Notification
```
