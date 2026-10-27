# Acadence - Student Academic & Examination Assistant

A modular, production-grade academic productivity and examination management web application built in Python. Designed to eliminate missed deadlines, examination clashes, and reactive exam preparation, while comprehensively demonstrating and evaluating 3rd-semester Data Structures and Algorithms coursework (**CO1, CO2, and CO3**).

Runs out of the box with **zero external dependencies** using Python's standard library.

---

## Technical Documentation Suite (`docs/`)

For complete system specifications, blueprints, and architectural deep-dives, explore the dedicated documentation suite:

| Document | Description |
| :--- | :--- |
| **[Architecture & System Design](docs/ARCHITECTURE.md)** | Multi-tier layered architecture, Mermaid sequence and component diagrams, design patterns (Memento, Facade, Strategy). |
| **[Backend Logic & Algorithms](docs/BACKEND_LOGIC_AND_ALGORITHMS.md)** | Mathematical formulas for Priority Scoring, Crisis Index triage rules, interval collision theorem, reverse sensitivity algebra, and Big-O master tables. |
| **[Database & Data Pipeline](docs/DATABASE_AND_DATA_PIPELINE.md)** | SQLite DDL schemas, Entity-Relationship Diagram (ERD), table constraints, relative-date dynamic seeding, and data lifecycle pipelines. |
| **[REST API Reference Manual](docs/API_REFERENCE.md)** | Complete endpoint specifications, HTTP methods, headers, request/response JSON schemas, and status codes. |
| **[Dependencies & Modules](docs/DEPENDENCIES_AND_MODULES.md)** | Zero-dependency philosophy, standard library module catalog, and optional visualization dependencies. |
| **[Replication & Setup Guide](docs/REPLICATION_AND_SETUP_GUIDE.md)** | Step-by-step reconstruction blueprint to rebuild the entire repository from scratch if deleted, verification checklists, and viva Q&A defense. |

---

## Course Outcome (CO) Mapping Matrix

| Course Outcome | Focus Topic | Project Implementation & File | Key Operations & DSA Complexity |
| :--- | :--- | :--- | :--- |
| **CO1** | Linear Data Structures (Stack & Queue) | • **Multi-Level Undo Engine** (`data_structures/stack.py`)<br>• **FIFO Academic Request Queue** (`data_structures/queue.py`) | • Stack: `push`, `pop`, `peek` in strict $\mathcal{O}(1)$ time. Reverses task mutations, status changes, and deletions.<br>• Queue: Linked-node queue with `_front` and `_rear` pointers for $\mathcal{O}(1)$ `enqueue` and `dequeue`. Compares FIFO request processing with priority task execution. |
| **CO2** | Linked Lists & Basic Searching | • **Custom Singly Linked List** (`data_structures/linked_list.py`)<br>• **Linear Search Traversal** (`algorithms/searching.py`)<br>• **Storage Benchmark** (`services/dsa_lab.py`) | • In-memory singly linked list storing dynamic task and exam nodes (`head` pointer, node traversal).<br>• Demonstrates $\mathcal{O}(1)$ head insertion vs. $\mathcal{O}(n)$ Python array shifting.<br>• Explains why linked lists incur $\mathcal{O}(n)$ sequential search overhead. |
| **CO3** | Searching & Sorting Performance Analysis | • **Manual Searching**: Linear Search & Binary Search (`algorithms/searching.py`)<br>• **Manual Sorting**: Bubble Sort, Insertion Sort, Merge Sort (`algorithms/sorting.py`)<br>• **Interactive DSA Lab** (`services/dsa_lab.py`) | • Binary search executes on sorted contiguous arrays in $\mathcal{O}(\log n)$ time using $\mathcal{O}(1)$ random-access middle indexing.<br>• Merge Sort ($\mathcal{O}(n \log n)$), Insertion Sort ($\mathcal{O}(n^2)$), and Bubble Sort ($\mathcal{O}(n^2)$) applied to rank tasks and sort exam schedules.<br>• Empirical benchmarks on scaling datasets ($N = 100$ to $5,000$). |

---

## System Architecture

```text
Acadence/
├── algorithms/
│   ├── __init__.py
│   ├── searching.py             # Manual Linear & Binary Search (CO2 & CO3)
│   └── sorting.py               # Manual Bubble, Insertion, & Merge Sort (CO3)
├── data_structures/
│   ├── __init__.py
│   ├── linked_list.py           # Custom Singly Linked List (CO2)
│   ├── node.py                  # Node class with data and next pointer
│   ├── queue.py                 # Custom FIFO Queue with front & rear pointers (CO1)
│   └── stack.py                 # Custom LIFO Stack (CO1)
├── database/
│   ├── __init__.py              # Database facade & public query interface
│   ├── connection.py            # SQLite connection manager & DB path
│   ├── operations.py            # CRUD operations for tasks, exams, assessments, requests
│   ├── schema.py                # Table schemas & teardown
│   └── seed.py                  # Realistic academic demo data seeder
├── models/
│   ├── __init__.py              # Central package export
│   ├── action.py                # UndoAction dataclass (LIFO Stack)
│   ├── assessment.py            # Assessment score dataclass
│   ├── exam.py                  # Exam dataclass
│   ├── request.py               # AcademicRequest dataclass (FIFO Queue)
│   ├── student.py               # Student profile dataclass
│   └── task.py                  # Task dataclass
├── services/
│   ├── __init__.py
│   ├── academic_planner.py      # Planner service with Stack Undo & daily study optimizer
│   ├── dsa_lab.py               # Empirical benchmarking suite (CO2 & CO3)
│   ├── exam_manager.py          # Exam service with schedule clash detector & countdown
│   ├── performance_analyzer.py  # Averages, decline detector & target score calculator
│   ├── priority_engine.py       # Transparent rule-based task prioritization formula
│   └── rescue_mode.py           # Academic Rescue triage engine
├── static/
│   ├── css/
│   │   └── style.css            # Responsive UI styling (dark & light modes)
│   └── js/
│       └── app.js               # Client-side controller & REST API connector
├── templates/
│   └── index.html               # Single-page web dashboard shell
├── tests/
│   ├── __init__.py
│   └── test_acadence.py         # 9 automated unit test suites
├── docs/                        # Complete technical documentation suite
│   ├── ARCHITECTURE.md          # Multi-tier design & sequence diagrams
│   ├── BACKEND_LOGIC_AND_ALGORITHMS.md # Formulas, triage, interval clashes, DSA
│   ├── DATABASE_AND_DATA_PIPELINE.md   # SQLite schema, ERD, and data lifecycles
│   ├── API_REFERENCE.md         # Comprehensive REST API manual
│   ├── DEPENDENCIES_AND_MODULES.md     # Standard library catalog & optional UI
│   └── REPLICATION_AND_SETUP_GUIDE.md  # Ground-up reconstruction blueprint
├── app.py                       # Zero-dependency full-stack server (http.server)
├── main.py                      # Interactive ANSI terminal CLI interface
├── streamlit_app.py             # Optional Streamlit interface
├── requirements.txt             # Optional dependencies for Streamlit
├── .gitignore                   # Comprehensive ignore rules
└── README.md                    # Master documentation & review guide
```

---

## Core Application Features

### 1. Unified Academic Dashboard
* **Next Exam Countdown**: Live real-time counter displaying days, hours, and minutes to the nearest scheduled examination.
* **Task Health Counters**: Visual metrics for Pending, In Progress, Completed, and Overdue tasks.
* **Schedule Clash Warning**: Immediate banner alert if overlapping examination slots are detected.
* **"What Should I Do Next?"**: Prominent, ranked list of top urgent tasks with transparent explanations detailing why each task was prioritized.
* **Academic Rescue Overview**: Live Crisis Score indicator (0 to 100) reflecting workload pressure.

### 2. Smart Academic Planner
* Add, update, delete, and filter academic tasks by subject and status.
* **Transparent Priority Scoring**:
  $$\text{Task Score} = \text{Urgency} + \text{Priority Weight} + \text{Subject Vulnerability Boost} + \text{Effort Factor}$$
* **Suggested Daily Study Schedule**: Input available study hours (e.g. 3.5 hours); the planner selects the optimal set of pending tasks fitting within the budget.
* **Multi-Level Undo**: Supported via a custom LIFO Stack to reverse accidental task deletions, updates, or status changes.

### 3. Examination Management
* Schedule exams with subject, date, time intervals, venue, revision completion progress, and syllabus.
* **Schedule Conflict Detector**: Pairwise algorithm checking interval overlaps ($\max(s_1, s_2) < \min(e_1, e_2)$) on identical dates to prevent exam clashes.
* **FIFO Academic Request Queue**: Linked-node queue where students submit requests (Hall tickets, Re-evaluations, Supplementary queries) processed in First-Come, First-Served order.

### 4. Academic Performance Analyzer
* Records scores across Quizzes, Assignments, Mid-Terms, Practicals, and Finals.
* **Decline Detection**: Rule-based detection that flags sudden drops ($\ge 10\%$) or consecutive downward trends.
* **Target Score Calculator**: Reverse sensitivity calculator computing the exact marks required on future assessments to achieve a desired overall average:
  $$\text{Required Marks} = \frac{\text{Target Average} \times W_{\text{new}} - \sum (\text{Marks}_i \times W_i)}{W_{\text{upcoming}}}$$
* **Revision Priorities**: Ranks subjects for review based on lowest average and exam proximity.

### 5. Flagship: Academic Rescue Mode
When facing multiple impending exams and backlog, Academic Rescue Mode calculates a **Crisis Index** (0 to 100) and executes triage:
* Identifies overdue assignments and tight deadlines ($< 48$ hours).
* Identifies subjects falling below the configurable warning threshold (default: $< 60\%$).
* Generates the top recommended action items with clear rationale.
* Features **One-Click Completion & Real-Time Recalculation** to recalculate priorities as tasks are finished.

### 6. Interactive DSA Performance Lab
* Allows selecting dataset sizes ($N = 100, 500, 1000, 2500, 5000$).
* Executes manual Linear Search, Binary Search, Bubble Sort, Insertion Sort, and Merge Sort.
* Measures empirical wall-clock time (`time.perf_counter()`), comparison counters, and swaps/moves.
* Compares Singly Linked List $\mathcal{O}(1)$ front insertion against Python array $\mathcal{O}(n)$ memory shifting.

---

## Report-Ready Complexity Reference Table

| Data Structure / Algorithm | Best Case | Average Case | Worst Case | Space Complexity | Real-World Application in Acadence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Custom LIFO Stack** | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ auxiliary | Multi-level Undo Engine for task mutations and deletions |
| **Custom FIFO Queue** | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ auxiliary | Academic Service Request Queue (Hall tickets, Re-evaluations) |
| **Singly Linked List** | $\mathcal{O}(1)$ [Head] | $\mathcal{O}(n)$ | $\mathcal{O}(n)$ | $\mathcal{O}(1)$ auxiliary | Dynamic memory storage of active study tasks and exams |
| **Linear Search** | $\mathcal{O}(1)$ | $\mathcal{O}(n)$ | $\mathcal{O}(n)$ | $\mathcal{O}(1)$ auxiliary | Sequential scanning of unsorted tasks and linked lists |
| **Binary Search** | $\mathcal{O}(1)$ | $\mathcal{O}(\log n)$ | $\mathcal{O}(\log n)$ | $\mathcal{O}(1)$ auxiliary | Fast lookup across pre-sorted exam dates and merit lists |
| **Bubble Sort** | $\mathcal{O}(n)$ [flag] | $\mathcal{O}(n^2)$ | $\mathcal{O}(n^2)$ | $\mathcal{O}(1)$ auxiliary | Comparison-based sorting benchmark |
| **Insertion Sort** | $\mathcal{O}(n)$ [sorted] | $\mathcal{O}(n^2)$ | $\mathcal{O}(n^2)$ | $\mathcal{O}(1)$ auxiliary | Fast incremental sorting for small batches of tasks |
| **Merge Sort** | $\mathcal{O}(n \log n)$ | $\mathcal{O}(n \log n)$ | $\mathcal{O}(n \log n)$ | $\mathcal{O}(n)$ auxiliary | Divide-and-conquer sorting for exam schedules and merit rankings |

---

## How to Run the Application

### Option 1: Full-Stack Web Application (Recommended, Zero External Dependencies)
Runs out of the box on standard Python 3.9+ without installing any third-party packages:
```bash
python3 app.py
```
Open your browser at:
```text
http://localhost:8080
```

### Option 2: Interactive Terminal CLI Interface
For a fast, menu-driven command-line experience with ANSI formatting:
```bash
python3 main.py
```

### Option 3: Streamlit Interface (Optional)
If you prefer running via Streamlit:
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Run Automated Unit Tests
```bash
python3 -m unittest discover tests
```
Runs 9 test suites validating Stack, Queue, Linked List, Algorithms, Priority Engine, Conflict Detector, and Undo functionality.

---

## Project Review & Demonstration Workflow

When presenting Acadence to professors or evaluators, use this recommended flow:

1. **Demonstrate the Dashboard**:
   * Point out the **Live Countdown** to the nearest exam.
   * Show the **Schedule Clash Alert** (demonstrating algorithmic interval collision detection).
   * Walk through the **"What Should I Do Next?"** recommendations and explain how the transparent rule-based Priority Engine calculated the order.

2. **Demonstrate the Smart Academic Planner (CO1 & CO2)**:
   * Add a new task or delete an existing task.
   * Click the **Undo** button in the top navigation bar to demonstrate the **LIFO Stack** reverting the operation in $\mathcal{O}(1)$ time.
   * Generate a **Daily Study Schedule** for 3.5 hours to show how the system selects tasks fitting within available time.

3. **Demonstrate Examinations & FIFO Queue (CO1)**:
   * View the scheduled exams sorted using **Merge Sort**.
   * Navigate to the **FIFO Academic Service Request Queue**: Enqueue a new request, then click "Process Next in Line" to show $\mathcal{O}(1)$ First-Come, First-Served dequeue processing.

4. **Demonstrate Academic Performance & Target Score Calculator**:
   * Show the subject cards and explain the **Decline Detection rule** (drop $\ge 10\%$ or negative trajectory).
   * Open the **Target Score Calculator**: Enter a target average of $85\%$ and show how reverse sensitivity analysis calculates the exact marks required on the upcoming exam.

5. **Demonstrate Flagship Feature: Academic Rescue Mode**:
   * Show the **Crisis Index gauge** and the top triage recommendations.
   * Click **"Mark Completed & Recalculate"** on the top recommendation to demonstrate real-time triage recalculation.

6. **Demonstrate the DSA Performance Lab (CO2 & CO3)**:
   * Select dataset size $N = 1000$.
   * Run the **Search Benchmark** to compare Linear Search vs. Binary Search ($\mathcal{O}(n)$ vs $\mathcal{O}(\log n)$).
   * Run the **Storage Benchmark** to show why Linked List front insertion ($\mathcal{O}(1)$ pointer updates) is significantly faster than Python array front insertion ($\mathcal{O}(n)$ memory shifting).
