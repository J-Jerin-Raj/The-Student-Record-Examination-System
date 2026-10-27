# Student Record & Examination Processing System (DSA Microproject)

A modular Python application designed for 3rd-semester Data Structures and Algorithms (DSA) coursework. It comprehensively satisfies **CO1, CO2, and CO3**, features empirical performance benchmarking, and introduces a novelty feature: the **What-If Marks Simulator & Academic Goal Planner**.

## Course Outcome (CO) Mapping Matrix

| Course Outcome | Focus Topic | Project Implementation | Key Operations | Time Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **CO1** | Linear Data Structures (Stack & Queue) | • **LIFO Undo Stack**: Multi-level undo for record mutations<br>• **FIFO Examination Queue**: Exam registration, hall tickets, re-evaluations | `push`, `pop`, `peek`<br>`enqueue`, `dequeue`, `peek` | Stack: $\mathcal{O}(1)$<br>Queue: $\mathcal{O}(1)$ |
| **CO2** | Linked List Data Structures & Sequential Search | • **Singly Linked List**: Primary record storage (`StudentNode`)<br>• **Linear Search**: Traversal on linked list to find students by ID/name<br>• **Storage Benchmark**: Comparison with Python List (Array) | Insert Head/Tail, Delete by ID, Update, Sequential Traversal | Search: $\mathcal{O}(n)$<br>Insert Head: $\mathcal{O}(1)$<br>Insert Tail: $\mathcal{O}(n)$ |
| **CO3** | Searching & Sorting Techniques & Performance Analysis | • **Searching**: Linear Search vs. Binary Search<br>• **Sorting**: Bubble Sort, Insertion Sort, Merge Sort<br>• **Ranking**: Merit list generation (by marks, name, ID)<br>• **Empirical Benchmark**: Runtime comparison across scaling datasets | Binary Search on sorted list, Bubble/Insertion/Merge sort | Linear: $\mathcal{O}(n)$<br>Binary: $\mathcal{O}(\log n)$<br>Merge: $\mathcal{O}(n \log n)$<br>Bubble/Insert: $\mathcal{O}(n^2)$ |
| **NOVELTY** | Academic Goal Seeking & Sensitivity Analysis | • **What-If Marks Simulator**: Performance bottleneck diagnosis, reverse sensitivity analysis to reach target percentages | Goal analysis, priority queue / headroom allocation | $\mathcal{O}(m \log m)$ for $m$ subjects |

---

## System Architecture & Directory Structure

```text
DSA-MicroProj/
├── algorithms/
│   ├── __init__.py
│   ├── searching.py             # Linear Search (LL & Array) and Binary Search (CO2 & CO3)
│   └── sorting.py               # Bubble Sort, Insertion Sort, Merge Sort (CO3)
├── structures/
│   ├── __init__.py
│   ├── node.py                  # Node class with data and next pointer
│   ├── linked_list.py           # Custom Singly Linked List (CO2)
│   ├── stack.py                 # Custom LIFO Stack (CO1)
│   └── queue.py                 # Custom FIFO Queue with front & rear pointers (CO1)
├── models/
│   ├── __init__.py
│   └── student.py               # Student dataclass with GPA, percentage, and grading
├── services/
│   ├── __init__.py
│   ├── student_manager.py       # Core service linking Linked List + Undo Stack
│   ├── exam_queue_manager.py    # Exam activities FIFO service (CO1)
│   └── what_if_simulator.py     # Novelty: What-If Marks Simulator & Goal Planner
├── benchmark/
│   ├── __init__.py
│   └── performance.py           # Empirical benchmarking suite (CO2 & CO3)
├── data/
│   └── sample_students.json     # Preloaded student dataset
├── tests/
│   ├── __init__.py
│   └── test_dsa.py              # 100% passing unit tests
├── web/
│   └── index.html               # Responsive Dark-mode Web UI
├── web_app.py                   # Zero-dependency local web server (http.server)
├── main.py                      # Interactive ANSI-colored CLI
└── README.md                    # Project documentation & review guide
```

---

## Core Data Structures & Algorithmic Analysis

### 1. Singly Linked List (`structures/linked_list.py`)
- **Design**: Composed of individual `Node` objects containing a `Student` instance and a `next` pointer.
- **Why used**: Demonstrates pointer manipulation and dynamic memory allocation without requiring contiguous blocks.
- **Operations**:
  - `insert_at_beginning(data)`: Updates head pointer in $\mathcal{O}(1)$ time.
  - `insert_at_end(data)`: Traverses to tail in $\mathcal{O}(n)$ time (or $\mathcal{O}(1)$ with tail pointer).
  - `delete_by_id(student_id)`: Unlinks matching node by tracking `prev.next = current.next` in $\mathcal{O}(n)$.
  - `search_by_id(student_id)`: Sequential linear traversal checking node data.

### 2. Custom Stack (`structures/stack.py`)
- **Design**: Dynamic array-backed LIFO (Last-In, First-Out) structure.
- **Role in Project**: Powering the **Multi-level Undo Engine**.
  - When a student is **Added**: An `ADD` action token is pushed. Undoing it deletes the newly added student.
  - When a student is **Updated**: A snapshot of the previous record is pushed. Undoing it restores the original values.
  - When a student is **Deleted**: The entire deleted `Student` object is pushed. Undoing it re-inserts the student.
- **Complexity**: `push()`, `pop()`, and `peek()` all run in strict $\mathcal{O}(1)$ time.

### 3. Custom Queue (`structures/queue.py`)
- **Design**: Implemented using linked nodes with dedicated `_front` and `_rear` pointers.
- **Why not `list.pop(0)`?**: Standard Python `list.pop(0)` takes $\mathcal{O}(n)$ time because all remaining elements must shift left in memory. Our custom linked Queue guarantees **strict $\mathcal{O}(1)$ time** for both `enqueue()` and `dequeue()`.
- **Role in Project**: Manages real-world examination activities (Exam Registrations, Hall Ticket Generation, Grade Re-evaluations, Supplementary Exams) on a First-Come, First-Served basis.

### 4. Searching Techniques (`algorithms/searching.py`)
- **Linear Search**: Sequentially scans elements one by one. Works on both unsorted linked lists and arrays. Time Complexity: $\mathcal{O}(n)$.
- **Binary Search**: Uses divide-and-conquer on sorted lists. Time Complexity: $\mathcal{O}(\log n)$.
- **Critical Technical Detail (Syllabus Note)**:
  > *Why not Binary Search on a Linked List?*
  > Binary search requires $\mathcal{O}(1)$ random access to the middle element (`arr[mid]`). On a singly linked list, reaching the middle requires traversing `n/2` pointers ($\mathcal{O}(n)$ steps), degrading binary search to $\mathcal{O}(n)$ or $\mathcal{O}(n \log n)$. Therefore, binary search is executed on contiguous array-backed storage for true $\mathcal{O}(\log n)$ efficiency.

### 5. Sorting Techniques (`algorithms/sorting.py`)
- **Bubble Sort ($\mathcal{O}(n^2)$)**: Adjacent element comparison with early-termination flag if no swaps occur.
- **Insertion Sort ($\mathcal{O}(n^2)$)**: Incrementally shifts elements to insert into the sorted partition. Excellent for small or nearly-sorted datasets.
- **Merge Sort ($\mathcal{O}(n \log n)$)**: Divide-and-conquer algorithm that recursively bisects arrays and merges sorted halves. Highly stable and consistent.
- **Flexibility**: All algorithms support sorting by **Marks** (Merit List), **Name**, or **Student ID** in either Ascending or Descending order.

---

## Novelty Feature: What-If Marks Simulator

The **What-If Marks Simulator** is an analytical decision-support engine for students:
1. **Performance Diagnostics**:
   - Identifies bottlenecks by categorizing subjects into:
     - *Critical* ($<50\%$): Risk of failure, fundamental remediation needed.
     - *Needs Improvement* ($50 - 69\%$): Significant gain margin.
     - *Proficient* ($70 - 84\%$): Solid foundation.
     - *Exemplary* ($\ge 85\%$): Mastery achieved.
2. **Reverse Sensitivity Goal Planning**:
   - Given a target overall percentage (e.g., $85\%$), computes the exact aggregate marks needed.
   - **Feasibility Verification**: Detects if the goal is mathematically possible (e.g., cannot exceed $100\%$ per subject).
   - **Smart Headroom Allocation**: Distributes needed marks using a greedy strategy prioritizing subjects with the largest gap (`100 - current_score`), maximizing return on study effort.
3. **Hypothetical Scenario Simulator**:
   - Evaluates "what-if" scores: *"If I score 92 in DSA and 88 in WebDev, what will my overall percentage and grade become?"*

---

## Big-O Performance Benchmarks

### Time & Space Complexity Summary Table

| Operation / Algorithm | Best Case | Average Case | Worst Case | Space Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **Stack Push / Pop** | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ auxiliary |
| **Queue Enqueue / Dequeue** | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ auxiliary |
| **Linked List Insert Head** | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ auxiliary |
| **Linked List Search** | $\mathcal{O}(1)$ | $\mathcal{O}(n)$ | $\mathcal{O}(n)$ | $\mathcal{O}(1)$ auxiliary |
| **Linear Search** | $\mathcal{O}(1)$ | $\mathcal{O}(n)$ | $\mathcal{O}(n)$ | $\mathcal{O}(1)$ auxiliary |
| **Binary Search** | $\mathcal{O}(1)$ | $\mathcal{O}(\log n)$ | $\mathcal{O}(\log n)$ | $\mathcal{O}(1)$ auxiliary |
| **Bubble Sort** | $\mathcal{O}(n)$ *(optimized)* | $\mathcal{O}(n^2)$ | $\mathcal{O}(n^2)$ | $\mathcal{O}(1)$ auxiliary |
| **Insertion Sort** | $\mathcal{O}(n)$ *(nearly sorted)* | $\mathcal{O}(n^2)$ | $\mathcal{O}(n^2)$ | $\mathcal{O}(1)$ auxiliary |
| **Merge Sort** | $\mathcal{O}(n \log n)$ | $\mathcal{O}(n \log n)$ | $\mathcal{O}(n \log n)$ | $\mathcal{O}(n)$ auxiliary |

### Empirical Findings: Singly Linked List vs. Python List (Array)
- **Head Insertion (`index 0`)**: Singly Linked List is significantly faster ($\approx 10\times - 30\times$) than Python List because the linked list only updates two pointers, whereas the array must shift all $N$ existing elements in memory.
- **Sequential Search**: Arrays benefit from CPU cache locality; linked lists have pointer-dereferencing overhead.

---

## How to Run the Application

### 1. Terminal / CLI Interface (Interactive Menu)
```bash
python3 main.py
```
Provides full menu-driven navigation with ANSI formatting for:
- CRUD operations on student records
- Undo stack operations
- Examination queue submissions and processing
- Sorting merit list generator
- What-If Marks Simulator
- Running live Big-O benchmarks

### 2. Interactive Web Dashboard (Zero External Dependencies)
```bash
python3 web_app.py
```
Then open your browser at:
```text
http://localhost:8080
```
*Features interactive graphical representations of the Linked List pointer chain, Undo Stack, Exam Queue, and dynamic What-If simulator gauges.*

### 3. Run Automated Unit Tests
```bash
python3 -m unittest discover tests
```
Runs 8 test suites covering Stack, Queue, Linked List, Undo Engine, Sorting, Searching, and the Simulator.

---

## Viva Voce & Review Q&A Preparation

**Q1: How is the undo feature implemented and what data structure makes it optimal?**  
*Answer:* Undo is implemented using a custom LIFO Stack. Every time a record is added, updated, or deleted, an inverse action token (containing snapshots of prior state) is pushed onto the stack. Calling "Undo" pops the top element in $\mathcal{O}(1)$ time and applies the inverse operation. Stack is optimal because undo operations must always reverse the *most recent* action first (LIFO order).

**Q2: Why did you implement the queue with linked nodes instead of `list.append()` and `list.pop(0)`?**  
*Answer:* In Python, `list.pop(0)` requires shifting all remaining elements to the left, resulting in $\mathcal{O}(n)$ time complexity per dequeue. Our custom queue uses linked nodes with separate `_front` and `_rear` pointers, ensuring both `enqueue` and `dequeue` operate in strict $\mathcal{O}(1)$ constant time.

**Q3: Why can't we efficiently run Binary Search on a Singly Linked List?**  
*Answer:* Binary search relies on accessing the middle element in $\mathcal{O}(1)$ time (`mid = (low + high) // 2`). In a singly linked list, accessing the $k$-th element requires sequentially traversing $k$ pointer steps from the head ($\mathcal{O}(k)$ time). This causes the recurrence relation to degrade to $\mathcal{O}(n)$ or $\mathcal{O}(n \log n)$, eliminating the logarithmic benefit. Hence, binary search is performed on contiguous array-backed storage.

**Q4: When would Insertion Sort be preferred over Merge Sort?**  
*Answer:* While Merge Sort has a superior worst-case time complexity ($\mathcal{O}(n \log n)$ vs $\mathcal{O}(n^2)$), Insertion Sort has very low constant factor overhead and runs in $\mathcal{O}(n)$ time on already-sorted or nearly-sorted data. Additionally, Insertion Sort is in-place ($\mathcal{O}(1)$ auxiliary space), whereas Merge Sort requires $\mathcal{O}(n)$ additional memory for temporary arrays.

**Q5: What is the novelty of your What-If Marks Simulator?**  
*Answer:* Most student systems are passive recording tools. The What-If Simulator provides proactive academic intelligence: it conducts reverse sensitivity analysis to calculate exactly how many marks a student must gain across specific subjects to achieve a target grade or percentage, verifying feasibility and prioritizing study effort where the improvement margin is highest.
