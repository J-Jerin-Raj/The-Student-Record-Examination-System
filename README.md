# Acadence - Student Academic & Examination Assistant

A comprehensive academic productivity and examination management web application built in Python. Designed to solve real student problems—eliminating missed deadlines, examination clashes, and reactive exam preparation—while implementing and evaluating 3rd-semester Data Structures and Algorithms coursework (**CO1, CO2, and CO3**).

---

## Problem Statement & Main Goal

College students often struggle to juggle overlapping examination schedules, assignment deadlines, and vulnerable subjects. Information is typically scattered across college notices, messy spreadsheets, and chat groups, leading to cramming and preventable academic penalties.

**Acadence** addresses this by providing an intelligent, centralized academic operations platform. It moves beyond standard CRUD student tracking by actively answering:
1. **What needs attention right now?**
2. **When does it need attention?**
3. **What concrete action should the student take next?**

The application features **Academic Rescue Mode**, an academic triage engine that evaluates urgency, priority, study effort, and subject performance vulnerability using deterministic, explainable rule-based scoring.

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
DSA-MicroProj/
├── data_structures/
│   ├── __init__.py
│   ├── node.py                  # Node class with data and next pointer
│   ├── stack.py                 # Custom LIFO Stack (CO1)
│   ├── queue.py                 # Custom FIFO Queue with front & rear pointers (CO1)
│   └── linked_list.py           # Custom Singly Linked List (CO2)
├── algorithms/
│   ├── __init__.py
│   ├── searching.py             # Manual Linear & Binary Search (CO2 & CO3)
│   └── sorting.py               # Manual Bubble, Insertion, & Merge Sort (CO3)
├── models.py                    # Structured dataclasses (Task, Exam, Assessment, UndoAction)
├── database.py                  # Persistent SQLite layer with schema & demo seeder
├── services/
│   ├── __init__.py
│   ├── priority_engine.py       # Transparent rule-based task prioritization formula
│   ├── academic_planner.py      # Planner service with Stack Undo & daily study optimizer
│   ├── exam_manager.py          # Exam service with schedule clash detector & countdown
│   ├── performance_analyzer.py  # Averages, decline detector & target score calculator
│   ├── rescue_mode.py           # Academic Rescue triage engine
│   └── dsa_lab.py               # Empirical benchmarking suite
├── static/
│   ├── style.css                # Modern responsive UI styling (dark/light modes)
│   └── app.js                   # Client-side controller & REST API connector
├── templates/
│   └── index.html               # Single-page application shell with collapsible sidebar
├── tests/
│   ├── __init__.py
│   └── test_acadence.py         # 9 automated unit test suites
├── app.py                       # Zero-dependency full-stack server (http.server)
├── streamlit_app.py             # Optional Streamlit interface
├── requirements.txt             # Optional dependencies for Streamlit
└── README.md                    # Project documentation & review guide
```

---

## Core Application Features

### 1. Unified Academic Dashboard
- **Next Exam Countdown**: Live real-time counter displaying days, hours, and minutes to the nearest scheduled examination.
- **Task Health Counters**: Visual metrics for Pending, In Progress, Completed, and Overdue tasks.
- **Schedule Clash Warning**: Immediate banner alert if overlapping examination slots are detected.
- **"What Should I Do Next?"**: Prominent, ranked list of top urgent tasks with transparent explanations detailing why each task was prioritized.
- **Academic Rescue Overview**: Live Crisis Score indicator (0 to 100) reflecting workload pressure.

### 2. Smart Academic Planner
- Add, update, delete, and filter academic tasks by subject and status.
- **Transparent Priority Scoring**:
  $$\text{Task Score} = \text{Urgency (hours to deadline)} + \text{Priority Weight} + \text{Subject Vulnerability Boost} + \text{Effort Factor}$$
- **Suggested Daily Study Schedule**: Input available study hours (e.g. 3.5 hours); the planner selects the optimal set of pending tasks fitting within the budget with clear rationale.
- **Multi-Level Undo**: Supported via a custom LIFO Stack to reverse accidental task deletions, updates, or status changes.

### 3. Examination Management
- Schedule exams with subject, date, time intervals, venue, revision completion progress, and syllabus.
- **Schedule Conflict Detector**: Pairwise algorithm checking interval overlaps ($\max(s_1, s_2) < \min(e_1, e_2)$) on identical dates to prevent exam clashes.
- **FIFO Academic Request Queue**: Linked-node queue where students submit requests (Hall tickets, Re-evaluations, Supplementary queries) processed in First-Come, First-Served order.

### 4. Academic Performance Analyzer
- Records scores across Quizzes, Assignments, Mid-Terms, Practicals, and Finals.
- **Decline Detection**: Rule-based detection that flags sudden drops ($\ge 10\%$) or consecutive downward trends.
- **Target Score Calculator**: Reverse sensitivity calculator computing the exact marks required on future assessments to achieve a desired overall average:
  $$\text{Required Marks} = \frac{\text{Target Average} \times W_{\text{new}} - \sum (\text{Marks}_i \times W_i)}{W_{\text{upcoming}}}$$
  Alerts the user if the target is already secured or mathematically unattainable ($> 100\%$).
- **Revision Priorities**: Ranks subjects for review based on lowest average and exam proximity.

### 5. Flagship: Academic Rescue Mode
When facing multiple impending exams and backlog, Academic Rescue Mode calculates a **Crisis Index** (0 to 100) and executes triage:
- Identifies overdue assignments and tight deadlines ($< 48$ hours).
- Identifies subjects falling below the configurable warning threshold (default: $< 60\%$).
- Generates the top recommended action items with clear rationale.
- Features **One-Click Completion & Real-Time Recalculation** to recalculate priorities as tasks are finished.

### 6. Interactive DSA Performance Lab
- Allows selecting dataset sizes ($N = 100, 500, 1000, 2500, 5000$).
- Executes manual Linear Search, Binary Search, Bubble Sort, Insertion Sort, and Merge Sort.
- Measures empirical wall-clock time (`time.perf_counter()`), comparison counters, and swaps/moves.
- Compares Singly Linked List $\mathcal{O}(1)$ front insertion against Python array $\mathcal{O}(n)$ memory shifting.

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

### Option 2: Streamlit Interface (Optional)
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
   - Point out the **Live Countdown** to the nearest exam.
   - Show the **Schedule Clash Alert** (demonstrating algorithmic interval collision detection).
   - Walk through the **"What Should I Do Next?"** recommendations and explain how the transparent rule-based Priority Engine calculated the order.

2. **Demonstrate the Smart Academic Planner (CO1 & CO2)**:
   - Add a new task or delete an existing task.
   - Click the **Undo** button in the top navigation bar to demonstrate the **LIFO Stack** reverting the operation in $\mathcal{O}(1)$ time.
   - Generate a **Daily Study Schedule** for 3.5 hours to show how the system selects tasks fitting within available time.

3. **Demonstrate Examinations & FIFO Queue (CO1)**:
   - View the scheduled exams sorted using **Merge Sort**.
   - Navigate to the **FIFO Academic Service Request Queue**: Enqueue a new request, then click "Process Next in Line" to show $\mathcal{O}(1)$ First-Come, First-Served dequeue processing.

4. **Demonstrate Academic Performance & Target Score Calculator**:
   - Show the subject cards and explain the **Decline Detection rule** (drop $\ge 10\%$ or negative trajectory).
   - Open the **Target Score Calculator**: Enter a target average of $85\%$ and show how reverse sensitivity analysis calculates the exact marks required on the upcoming exam.

5. **Demonstrate Flagship Feature: Academic Rescue Mode**:
   - Show the **Crisis Index gauge** and the top triage recommendations.
   - Click **"Mark Completed & Recalculate"** on the top recommendation to demonstrate real-time triage recalculation.

6. **Demonstrate the DSA Performance Lab (CO2 & CO3)**:
   - Select dataset size $N = 1000$.
   - Run the **Search Benchmark** to compare Linear Search vs. Binary Search ($\mathcal{O}(n)$ vs $\mathcal{O}(\log n)$).
   - Run the **Storage Benchmark** to show why Linked List front insertion ($\mathcal{O}(1)$ pointer updates) is significantly faster than Python array front insertion ($\mathcal{O}(n)$ memory shifting).

---

## Viva Voce Preparation Q&A

**Q1: How does your undo mechanism work, and why is a Stack the optimal data structure?**  
*Answer:* Undo is implemented using the Command/Snapshot pattern on a custom LIFO Stack (`data_structures/stack.py`). Whenever a task or record is created, edited, deleted, or toggled, an inverted `UndoAction` snapshot is pushed onto the stack. When the student clicks Undo, the most recent action is popped in $\mathcal{O}(1)$ time and reversed. A Stack is mathematically optimal because undo operations must always reverse the *latest* operation first (LIFO order).

**Q2: Why did you build the Queue using linked nodes rather than Python's built-in `list.pop(0)`?**  
*Answer:* In Python, `list.pop(0)` requires shifting all subsequent $N-1$ elements in memory, causing an $\mathcal{O}(n)$ performance penalty per dequeue. Our custom queue uses linked nodes with separate `_front` and `_rear` pointers, ensuring that both `enqueue()` and `dequeue()` execute in strict $\mathcal{O}(1)$ constant time.

**Q3: Why can't Binary Search be applied efficiently directly on a Singly Linked List?**  
*Answer:* Binary search requires random access to the middle element in $\mathcal{O}(1)$ time (`arr[mid]`). In a singly linked list, elements are scattered across dynamic memory and linked via pointers; accessing node $k$ requires sequentially traversing $k$ pointer steps from `head` ($\mathcal{O}(k)$ time). This degrades binary search to $\mathcal{O}(n)$ or $\mathcal{O}(n \log n)$, defeating the logarithmic advantage. Thus, binary search is executed on contiguous array-backed storage.

**Q4: How does your examination schedule conflict detection work?**  
*Answer:* The conflict detector (`services/exam_manager.py`) checks all pairs of exams on identical dates. For exams with time intervals $[s_1, e_1]$ and $[s_2, e_2]$, an overlap exists if and only if:
$$\max(s_1, s_2) < \min(e_1, e_2)$$
If true, the system flags the exact clashing subjects, venues, and colliding duration.

**Q5: What makes Academic Rescue Mode more than a standard to-do list?**  
*Answer:* Standard to-do lists order tasks only by manual due dates or static tags. Academic Rescue Mode is an academic triage engine: it computes a composite Rescue Score considering deadline proximity, task priority, subject vulnerability (penalty boost if student's average in that subject is $< 60\%$), and effort feasibility. It provides clear, explainable rationale for why each task is recommended first.
