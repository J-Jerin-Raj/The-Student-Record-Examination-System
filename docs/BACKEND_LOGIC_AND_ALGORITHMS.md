# Acadence - Backend Logic & Algorithmic Foundations

This document provides a comprehensive technical breakdown of all algorithms, mathematical formulations, and custom data structures implemented across the Acadence backend.

---

## 1. The Priority Engine Formulation (`services/priority_engine.py`)

The **Priority Engine** calculates a deterministic, explainable priority score for every academic task to answer the question: *"What concrete action should the student take next?"*

### 1.1 Mathematical Formula

$$\text{Total Priority Score} = S_{\text{urgency}} + S_{\text{priority}} + S_{\text{vulnerability}} + S_{\text{effort}}$$

Where each component is defined as follows:

#### A. Urgency Component ($S_{\text{urgency}}$)
Based on hours remaining until deadline ($\Delta t = t_{\text{deadline}} - t_{\text{now}}$):

$$S_{\text{urgency}} = 
\begin{cases} 
80 + \min(20, \frac{|\Delta t|}{24} \times 10) & \text{if } \Delta t < 0 \text{ (Overdue Task)} \\
60 - (\frac{\Delta t}{24} \times 20) & \text{if } 0 \le \Delta t \le 24 \text{ (Due within 24 hours)} \\
40 - (\frac{\Delta t - 24}{24} \times 10) & \text{if } 24 < \Delta t \le 48 \text{ (Due within 48 hours)} \\
20 - (\frac{\Delta t - 48}{120} \times 15) & \text{if } 48 < \Delta t \le 168 \text{ (Due within 7 days)} \\
5 & \text{if } \Delta t > 168 \text{ (Due in > 7 days)} 
\end{cases}$$

* **Design Rationale**: Overdue tasks immediately jump to an 80+ baseline with an escalating penalty for each day overdue. Tasks due within 24 hours receive an elevated score to prevent missed submissions.

#### B. Explicit Priority Component ($S_{\text{priority}}$)
Maps user-assigned priority categories to numeric weights:

$$S_{\text{priority}} = 
\begin{cases} 
40 & \text{if Priority} = \text{"Critical"} \\
30 & \text{if Priority} = \text{"High"} \\
20 & \text{if Priority} = \text{"Medium"} \\
10 & \text{if Priority} = \text{"Low"} 
\end{cases}$$

#### C. Academic Vulnerability Component ($S_{\text{vulnerability}}$)
Injects academic context into task management. If a student is failing or struggling in a subject, tasks in that subject receive a priority boost:

$$S_{\text{vulnerability}} = 
\begin{cases} 
35 & \text{if Subject Average} < 50\% \text{ (Critical Risk)} \\
20 & \text{if } 50\% \le \text{Subject Average} < \text{Threshold} \text{ (Vulnerable)} \\
0 & \text{if Subject Average} \ge \text{Threshold or No Data} 
\end{cases}$$

#### D. Effort & Feasibility Component ($S_{\text{effort}}$)
Rewards "quick wins" to maintain study momentum:

$$S_{\text{effort}} = 
\begin{cases} 
15 & \text{if Estimated Effort} \le 1.5 \text{ hours} \\
10 & \text{if } 1.5 < \text{Estimated Effort} \le 3.0 \text{ hours} \\
5 & \text{if } 3.0 < \text{Estimated Effort} \le 5.0 \text{ hours} \\
0 & \text{if Estimated Effort} > 5.0 \text{ hours} 
\end{cases}$$

### 1.2 Explainable Rationale Generation
The engine doesn't just output a number; it synthesizes a plain-language explanation (e.g., `"Overdue by 24h | Marked as Critical | Subject average is vulnerable (48.0%)"`). This transparency builds student trust and evaluator confidence.

---

## 2. Academic Rescue Mode & Crisis Index (`services/rescue_mode.py`)

Academic Rescue Mode acts as an automated triage officer during high-stress periods (e.g., midterms or finals).

### 2.1 Crisis Index Formula (0 to 100)

$$\text{Crisis Index} = \min\left(100, \; C_{\text{overdue}} + C_{\text{vulnerable}} + C_{\text{imminent}}\right)$$

Where:
* $C_{\text{overdue}} = \min(40.0, \; N_{\text{overdue}} \times 15.0)$
* $C_{\text{vulnerable}} = \min(35.0, \; N_{\text{vulnerable\_subjects}} \times 12.0)$
* $C_{\text{imminent}} = \min(25.0, \; N_{\text{exams\_within\_10\_days}} \times 8.0)$

### 2.2 Triage Classifications

| Crisis Index | Classification | Action Mandate |
| :---: | :--- | :--- |
| **$\ge 70$** | **Severe Academic Pressure** | Take immediate action: Freeze low-priority tasks, clear overdue items first, focus strictly on top 3 triage cards. |
| **$40 - 69$** | **Moderate Workload Warning** | Prioritize tasks due in the next 48 hours and reinforce vulnerable subjects. |
| **$< 40$** | **Stable Academic Standing** | Workload is balanced and manageable. Maintain standard study pace. |

---

## 3. Examination Schedule Clash Detector (`services/exam_manager.py`)

### 3.1 Interval Collision Theorem
Two scheduled examinations $E_1$ with time window $[s_1, e_1]$ and $E_2$ with time window $[s_2, e_2]$ clash if and only if they occur on the **same calendar date** and their open intervals overlap:

$$\text{Collision}(E_1, E_2) \iff (\text{Date}_1 = \text{Date}_2) \land \left(\max(s_1, s_2) < \min(e_1, e_2)\right)$$

### 3.2 Algorithmic Implementation & Complexity
```python
for i in range(len(exams)):
    for j in range(i + 1, len(exams)):
        if exams[i].exam_date == exams[j].exam_date:
            s1, e1 = parse_time(exams[i])
            s2, e2 = parse_time(exams[j])
            if max(s1, s2) < min(e1, e2):
                record_clash(exams[i], exams[j])
```
* **Time Complexity**: $\mathcal{O}(n^2)$ pairwise comparison where $n$ is the number of scheduled exams. For institutional scale ($n > 1000$), exams are pre-bucketed by date into a hash map, reducing time complexity to $\mathcal{O}(n \log n)$ via interval trees or sorting.
* **Space Complexity**: $\mathcal{O}(k)$ auxiliary space where $k$ is the number of detected clashes.

---

## 4. Reverse Sensitivity Analysis for Target Scores (`services/performance_analyzer.py`)

Given a student's prior assessments and a desired overall subject average $A_{\text{target}}$, this engine calculates the exact score required on an upcoming assessment.

### 4.1 Mathematical Derivation
Let existing assessments have percentages $P_1, P_2, \dots, P_k$ with corresponding weights $W_1, W_2, \dots, W_k$.  
Let the upcoming assessment have weight $W_{\text{upcoming}}$ and maximum marks $M_{\text{max}}$.  
We seek the required percentage score $P_{\text{req}}$ such that:

$$A_{\text{target}} = \frac{\sum_{i=1}^{k} (P_i \times W_i) + (P_{\text{req}} \times W_{\text{upcoming}})}{\sum_{i=1}^{k} W_i + W_{\text{upcoming}}}$$

Solving for $P_{\text{req}}$:

$$P_{\text{req}} = \frac{A_{\text{target}} \times \left(\sum_{i=1}^{k} W_i + W_{\text{upcoming}}\right) - \sum_{i=1}^{k} (P_i \times W_i)}{W_{\text{upcoming}}}$$

The required raw marks $M_{\text{req}}$:

$$M_{\text{req}} = \text{round}\left(\frac{P_{\text{req}}}{100.0} \times M_{\text{max}}, \; 1\right)$$

### 4.2 Feasibility Boundary Conditions
* **Achieved**: If $P_{\text{req}} \le 0$, the student has mathematically already secured the target average even with a 0 score.
* **Achievable**: If $0 < P_{\text{req}} \le 100.0$, the target is mathematically feasible.
* **Unachievable**: If $P_{\text{req}} > 100.0$, the target is impossible. The engine calculates the **maximum attainable ceiling score** assuming a perfect 100% on the final.

---

## 5. Daily Study Schedule Packing Algorithm (`services/academic_planner.py`)

Given an available daily study budget of $H$ hours:
1. All pending tasks are ranked descending by their `Priority Score` from the Priority Engine.
2. A greedy packing loop iterates through the sorted tasks.
3. A task is admitted if:
   $$\text{Allocated Hours} + \text{Effort} \le H + 0.5 \text{ hours (Flexibility buffer)}$$
4. Output: Structured daily time-blocks with cumulative study metrics.

---

## 6. Core Custom Data Structures (CO1 & CO2)

### 6.1 Custom LIFO Stack (`data_structures/stack.py`) - CO1
* **Role**: Powers the Multi-Level Undo Engine.
* **Invertible Action Tokens (`UndoAction`)**:
  * `CREATE`: Undoing deletes the newly created entity.
  * `UPDATE`: Undoing restores `previous_state` snapshot.
  * `DELETE`: Undoing re-inserts the deleted entity snapshot.
  * `STATUS_CHANGE`: Undoing toggles the status back to previous.
* **Complexity**: `push()`, `pop()`, and `peek()` run in strict $\mathcal{O}(1)$ time.

### 6.2 Custom FIFO Queue (`data_structures/queue.py`) - CO1
* **Design**: Implemented using linked `Node` objects with explicit `_front` and `_rear` pointers.
* **Why not Python `list.pop(0)`?**:
  * Standard Python lists are contiguous arrays. Calling `list.pop(0)` shifts all remaining $n-1$ elements in memory, requiring $\mathcal{O}(n)$ time per dequeue.
  * Our custom linked Queue guarantees **strict $\mathcal{O}(1)$ time** for both `enqueue()` and `dequeue()`.
* **Role**: Manages student academic service requests (Hall Tickets, Re-evaluations, Doubts) in First-Come, First-Served order.

### 6.3 Singly Linked List (`data_structures/linked_list.py`) - CO2
* **Design**: Dynamic node allocation with `head` pointer and integer size counter.
* **Operations**:
  * `insert_front(data)`: Updates head pointer in $\mathcal{O}(1)$ time without contiguous memory reallocation.
  * `insert_rear(data)`: Traverses to tail in $\mathcal{O}(n)$ time.
  * `delete_by_id(id)`: Traverses and unlinks matching node in $\mathcal{O}(n)$ time.
  * `search_by_id(id)`: Sequential linear scan returning item and exact comparison count.

---

## 7. Searching & Sorting Algorithms (CO3)

### 7.1 Searching Suite (`algorithms/searching.py`)
1. **Linear Search**: Sequentially inspects elements one by one. Time Complexity: Best $\mathcal{O}(1)$, Worst $\mathcal{O}(n)$.
2. **Binary Search**: Divide-and-conquer on pre-sorted arrays. Time Complexity: $\mathcal{O}(\log n)$.
3. **Critical Syllabus Insight**:
   > *Why cannot Binary Search run in $\mathcal{O}(\log n)$ on a Singly Linked List?*  
   > Binary search requires $\mathcal{O}(1)$ random access to the midpoint element (`arr[mid]`). On a linked list, navigating to node `mid` requires sequentially chasing $k = n/2$ pointers from the head ($\mathcal{O}(n)$ steps), degrading binary search to $\mathcal{O}(n)$ or $\mathcal{O}(n \log n)$. Hence, binary search is executed on contiguous array-backed storage.

### 7.2 Sorting Suite (`algorithms/sorting.py`)
1. **Bubble Sort**: Comparison-based adjacent swap algorithm. Features an **early-termination flag** (`swapped = False`) enabling $\mathcal{O}(n)$ best-case runtime on already-sorted arrays.
2. **Insertion Sort**: Incremental sorting that shifts elements to insert keys into their correct sorted position. Features low constant factors, optimal for small datasets ($N \le 50$) or nearly-sorted inputs.
3. **Merge Sort**: Stable divide-and-conquer algorithm that recursively halves arrays and merges sorted sub-arrays. Guarantees $\mathcal{O}(n \log n)$ in best, average, and worst cases.

### 7.3 Asymptotic Complexity Master Table

| Algorithm / Data Structure | Best Case | Average Case | Worst Case | Auxiliary Space | Stable? |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Stack Push / Pop** | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | N/A |
| **Queue Enqueue / Dequeue** | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | N/A |
| **Linked List Head Insertion** | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | N/A |
| **Linear Search** | $\mathcal{O}(1)$ | $\mathcal{O}(n)$ | $\mathcal{O}(n)$ | $\mathcal{O}(1)$ | N/A |
| **Binary Search** | $\mathcal{O}(1)$ | $\mathcal{O}(\log n)$ | $\mathcal{O}(\log n)$ | $\mathcal{O}(1)$ | N/A |
| **Bubble Sort** | $\mathcal{O}(n)$ | $\mathcal{O}(n^2)$ | $\mathcal{O}(n^2)$ | $\mathcal{O}(1)$ | Yes |
| **Insertion Sort** | $\mathcal{O}(n)$ | $\mathcal{O}(n^2)$ | $\mathcal{O}(n^2)$ | $\mathcal{O}(1)$ | Yes |
| **Merge Sort** | $\mathcal{O}(n \log n)$ | $\mathcal{O}(n \log n)$ | $\mathcal{O}(n \log n)$ | $\mathcal{O}(n)$ | Yes |
