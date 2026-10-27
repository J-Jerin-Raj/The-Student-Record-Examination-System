# Acadence - Complete System Replication & Setup Guide

This guide is an end-to-end blueprint. If the codebase is lost, corrupted, or deleted, following this document will reconstruct the entire application, its database schema, algorithms, services, and web dashboard from scratch.

---

## 1. Prerequisites & Environment Setup

* **Runtime**: Python 3.9 or higher (standard installation from [python.org](https://www.python.org)).
* **Operating System**: Platform-agnostic (Windows 10/11, macOS, Ubuntu/Debian/Arch Linux).
* **Network / Internet**: None required for core application (zero external packages).

```bash
# Verify Python installation
python3 --version  # Or 'python --version' on Windows
```

---

## 2. Directory Tree Scaffolding

To recreate the directory hierarchy from scratch, execute:

### On Unix / macOS (Bash / Zsh):
```bash
mkdir -p Acadence/{algorithms,data_structures,database,models,services,static/css,static/js,templates,tests,docs}
cd Acadence
```

### On Windows (PowerShell):
```powershell
New-Item -ItemType Directory -Force -Path `
  algorithms, data_structures, database, models, services, `
  static\css, static\js, templates, tests, docs
```

---

## 3. Step-by-Step Code Generation Blueprint

When regenerating the codebase, follow this strict dependency-ordered sequence:

### Phase 1: Core Data Structures (`data_structures/`)
Implement in this exact order to avoid import circularity:
1. **`node.py`**: Create `Node(data, next_node=None)`.
2. **`stack.py`**: Create `Stack(capacity=None)` with `push()`, `pop()`, `peek()`, `is_empty()`, `size()`. Enforce $\mathcal{O}(1)$ operations and raise `OverflowError` / `IndexError`.
3. **`queue.py`**: Create `Queue(capacity=None)` using linked nodes with `_front` and `_rear` pointers for $\mathcal{O}(1)$ `enqueue()` and `dequeue()`.
4. **`linked_list.py`**: Create `SinglyLinkedList()` with `insert_front()` ($\mathcal{O}(1)$), `insert_rear()` ($\mathcal{O}(n)$), `delete_by_id()` ($\mathcal{O}(n)$), `search_by_id()` ($\mathcal{O}(n)$), and `to_list()`.
5. **`__init__.py`**: Re-export `Node`, `Stack`, `Queue`, `SinglyLinkedList`.

### Phase 2: Domain Entities (`models/`)
Create dataclasses matching the schema:
1. **`task.py`**: `@dataclass class Task` (fields: `id`, `title`, `subject`, `task_type`, `deadline`, `estimated_effort`, `priority`, `status`, `notes`, `created_at`). Include `to_dict()` and `from_dict()`.
2. **`exam.py`**: `@dataclass class Exam` (fields: `id`, `subject`, `exam_date`, `start_time`, `end_time`, `venue`, `syllabus`, `revision_progress`, `priority`, `created_at`).
3. **`assessment.py`**: `@dataclass class Assessment` (fields: `id`, `subject`, `assessment_name`, `assessment_type`, `max_marks`, `marks_obtained`, `weightage`, `assessment_date`, `notes`). Include `@property percentage`.
4. **`request.py`**: `@dataclass class AcademicRequest` (fields: `id`, `request_id`, `student_name`, `request_type`, `subject`, `details`, `status`, `created_at`).
5. **`action.py`**: `@dataclass class UndoAction` (fields: `entity_type`, `action_type`, `entity_id`, `previous_state`, `new_state`, `description`).
6. **`student.py`**: `@dataclass class Student` with `@property percentage` and `@property grade`.
7. **`__init__.py`**: Re-export all model classes.

### Phase 3: Algorithms Core (`algorithms/`)
1. **`searching.py`**: Implement `linear_search()` ($\mathcal{O}(n)$ scan with comparison counting) and `binary_search()` ($\mathcal{O}(\log n)$ divide-and-conquer on sorted lists). Encapsulate outputs in `@dataclass SearchResult`.
2. **`sorting.py`**: Implement `bubble_sort()` (with early exit swap flag), `insertion_sort()` (with shift counters), and `merge_sort()` (recursive divide-and-conquer). Encapsulate outputs in `@dataclass SortResult`.
3. **`__init__.py`**: Re-export algorithms.

### Phase 4: Database Layer (`database/`)
1. **`connection.py`**: Configure `get_connection()` using `sqlite3.connect(DB_PATH)` with `row_factory = sqlite3.Row`.
2. **`schema.py`**: Implement `init_db()` creating `tasks`, `exams`, `assessments`, `academic_requests`, and `settings` tables. Implement `clear_all_data()`.
3. **`seed.py`**: Implement `seed_demo_data()` using relative timestamps (`now + timedelta(...)`) to seed all 5 courses, declining OS marks, clash demo, and overdue tasks.
4. **`operations.py`**: Implement CRUD functions (`get_all_tasks`, `insert_task`, `update_task`, `delete_task`, `get_all_exams`, `insert_exam`, `get_all_assessments`, etc.).
5. **`__init__.py`**: Facade exposing all database functions.

### Phase 5: Business Services (`services/`)
1. **`priority_engine.py`**: Implement `PriorityEngine` with weights: Urgency (up to 100), Priority (up to 40), Vulnerability (up to 35), Effort (up to 15).
2. **`academic_planner.py`**: Implement `AcademicPlannerService` linking SQLite tasks with `Stack` (Undo) and `SinglyLinkedList`. Include `get_suggested_daily_schedule()`.
3. **`exam_manager.py`**: Implement `ExamManagerService` linking exams with `Queue` (Academic Requests) and `detect_conflicts()` ($\max(s_1, s_2) < \min(e_1, e_2)$).
4. **`performance_analyzer.py`**: Implement `PerformanceAnalyzerService` for subject averages, decline warnings (drop $\ge 10\%$), and `calculate_required_score()`.
5. **`rescue_mode.py`**: Implement `AcademicRescueService.analyze_rescue_state()` computing the `Crisis Index` (0 to 100).
6. **`dsa_lab.py`**: Implement `DSALabService` benchmarking search, sort, and linked list vs array.
7. **`__init__.py`**: Re-export all service classes.

### Phase 6: Presentation Interfaces
1. **`app.py`**: Build `AcadenceRequestHandler(BaseHTTPRequestHandler)` dispatching all REST endpoints and serving static assets.
2. **`main.py`**: Build `AcadenceCLIController` providing menu-driven terminal navigation with ANSI styling.
3. **`templates/index.html`**: Build responsive single-page application shell.
4. **`static/css/style.css`**: Dark/light theme design system.
5. **`static/js/app.js`**: Frontend controller managing API AJAX requests and dynamic DOM updates.

---

## 4. Verification & Testing Checklist

Execute these verification commands sequentially:

### Step 1: Run Unit Tests
```bash
python3 -m unittest discover tests
```
* **Expected Result**: `Ran 9 tests in ~0.14s -> OK`.
* Validates Stack LIFO, Queue FIFO, Linked List CRUD, Search/Sort complexities, Priority Engine, and Conflict Detector.

### Step 2: Test Interactive Terminal CLI
```bash
python3 main.py
```
* **Verify**: Choose Option `1` (Dashboard) and Option `7` (Run DSA Benchmarks) to ensure all services hydrate correctly.

### Step 3: Launch Full-Stack Web Application
```bash
python3 app.py
```
* Open your web browser at:
  ```text
  http://localhost:8080
  ```
* **Verify**:
  1. Dashboard displays countdown timer and crisis index gauge.
  2. Navigate to "Smart Planner", add a task, then click "Undo" in the top bar to verify the LIFO Stack.
  3. Navigate to "Examinations", check for collision alerts.
  4. Navigate to "FIFO Service Queue", submit a request, and process it.
  5. Navigate to "Performance", run the target score calculator.
  6. Navigate to "DSA Lab", run live empirical benchmarking trials.

---

## 5. Viva Voce & Evaluation Defense Preparation

| Evaluation Question | Optimal Examiner Answer |
| :--- | :--- |
| **Q1: Why use a custom Linked Queue instead of a Python List?** | *Answer:* In Python, calling `list.pop(0)` takes $\mathcal{O}(n)$ time because all subsequent memory blocks must shift left. Our custom Queue uses linked nodes with separate `_front` and `_rear` pointers, guaranteeing strict $\mathcal{O}(1)$ constant-time enqueue and dequeue. |
| **Q2: How is the Multi-Level Undo feature optimal?** | *Answer:* It implements the Memento/Command pattern using an array-backed LIFO Stack. Operations must reverse in exact reverse chronological order. Each push/pop operates in $\mathcal{O}(1)$ time, storing inverse mutation tokens. |
| **Q3: Why can't Binary Search run in $\mathcal{O}(\log n)$ on a Linked List?** | *Answer:* Binary search relies on $\mathcal{O}(1)$ random-access middle indexing (`arr[mid]`). On a singly linked list, accessing the middle element requires sequentially traversing $n/2$ pointers ($\mathcal{O}(n)$ steps), degrading binary search to $\mathcal{O}(n)$ or $\mathcal{O}(n \log n)$. |
| **Q4: How does the Conflict Detector determine exam clashes?** | *Answer:* It tests the open interval overlap condition: two exams on the same date clash if and only if $\max(\text{start}_1, \text{start}_2) < \min(\text{end}_1, \text{end}_2)$. |
| **Q5: How does the Priority Engine prevent missed deadlines?** | *Answer:* It applies deterministic piecewise urgency scoring. Overdue tasks automatically enter an escalating 80+ score bracket, while impending deadlines (< 24h) and tasks in academically vulnerable subjects receive priority boosts. |
