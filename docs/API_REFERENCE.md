# Acadence - REST API Reference Manual

The Acadence REST API is powered entirely by Python standard library `http.server.HTTPServer` with zero third-party dependencies.

* **Base URL**: `http://localhost:8080`
* **Content-Type**: `application/json`
* **Cross-Origin**: Enabled (`Access-Control-Allow-Origin: *`)

---

## Table of Contents
1. [Dashboard & Analytics](#1-dashboard--analytics)
2. [Task Management & Smart Planner](#2-task-management--smart-planner)
3. [Undo Engine (CO1 LIFO Stack)](#3-undo-engine-co1-lifo-stack)
4. [Examination & Schedule Management (CO3)](#4-examination--schedule-management-co3)
5. [Academic Service Queue (CO1 FIFO Queue)](#5-academic-service-queue-co1-fifo-queue)
6. [Academic Performance & Target Calculator](#6-academic-performance--target-calculator)
7. [Academic Rescue Mode](#7-academic-rescue-mode)
8. [DSA Performance Lab (CO2 & CO3)](#8-dsa-performance-lab-co2--co3)
9. [System Configuration & Admin](#9-system-configuration--admin)

---

## 1. Dashboard & Analytics

### `GET /api/dashboard`
Aggregates a complete high-level snapshot across all subsystems for the main dashboard view.

* **Request**: `GET /api/dashboard`
* **Response Status**: `200 OK`
* **Response Payload Example**:
```json
{
  "task_metrics": {
    "total": 6,
    "pending": 4,
    "in_progress": 1,
    "completed": 1,
    "overdue": 1
  },
  "next_exam_countdown": {
    "exam": {
      "id": 1,
      "subject": "Data Structures & Algorithms",
      "exam_date": "2026-10-31",
      "start_time": "09:30",
      "end_time": "12:30",
      "venue": "Exam Hall B-101"
    },
    "days": 3,
    "hours": 11,
    "minutes": 14,
    "total_hours": 83.2,
    "is_imminent": false
  },
  "exam_conflicts": [
    {
      "date": "2026-11-15",
      "clashing_subjects": ["Data Structures & Algorithms", "Operating Systems"],
      "slot1": "Data Structures & Algorithms: 09:30 - 12:30 (Exam Hall B-101)",
      "slot2": "Operating Systems: 11:00 - 14:00 (Auditorium 2)",
      "severity": "Critical Clash"
    }
  ],
  "performance_summary": {
    "overall_average": 75.8,
    "overall_grade": "A (Very Good)",
    "vulnerable_subjects_count": 1
  },
  "rescue_summary": {
    "crisis_index": 43.0,
    "status_level": "Moderate Workload Warning",
    "action_statement": "Prioritize tasks due in the next 48 hours and reinforce vulnerable subjects."
  },
  "what_to_do_next": [
    {
      "task": {
        "id": 3,
        "title": "Process Scheduling Simulation Lab Report",
        "subject": "Operating Systems",
        "deadline": "2026-10-26 21:00",
        "estimated_effort": 2.5
      },
      "score": 158.0,
      "rationale": "Overdue by 24.1 hours | Marked as Critical priority | Quick win (2.5h estimated)",
      "is_overdue": true,
      "hours_remaining": -24.1
    }
  ]
}
```

---

## 2. Task Management & Smart Planner

### `GET /api/tasks`
Retrieves tasks ranked by the Priority Engine. Supports optional query parameters.

* **Query Parameters**:
  * `status`: Filter by status (`Pending`, `In Progress`, `Completed`).
  * `subject`: Filter by subject name.
* **Response Status**: `200 OK`
* **Response Schema**:
```json
[
  {
    "id": 1,
    "title": "Implement Binary Search Tree Balancing",
    "subject": "Data Structures & Algorithms",
    "task_type": "Assignment",
    "deadline": "2026-10-28 14:00",
    "estimated_effort": 3.5,
    "priority": "Critical",
    "status": "In Progress",
    "notes": "Need to complete AVL rotations",
    "priority_score": 122.6,
    "is_overdue": false,
    "hours_remaining": 16.5,
    "rationale": "Due soon (within 2 days) | Marked as Critical priority"
  }
]
```

### `POST /api/tasks`
Creates a new task and pushes an invertible snapshot to the LIFO Undo Stack.

* **Request Body**:
```json
{
  "title": "Graph Theory Practice Sheet",
  "subject": "Discrete Mathematics",
  "task_type": "Assignment",
  "deadline": "2026-11-02 23:59",
  "estimated_effort": 3.0,
  "priority": "Medium",
  "notes": "Eulerian circuit proofs"
}
```
* **Response**: `201 Created`
```json
{
  "success": true,
  "message": "Task created successfully.",
  "id": 7
}
```

### `POST /api/tasks/<id>/status`
Updates task execution status.

* **Request Body**: `{"status": "Completed"}`
* **Response**: `200 OK`
```json
{
  "success": true,
  "message": "Task status updated to 'Completed'."
}
```

### `GET /api/planner/daily-schedule`
Computes an optimal study schedule packed within available hours.

* **Query Parameters**: `hours=3.5`
* **Response**: `200 OK`
```json
{
  "available_hours": 3.5,
  "allocated_hours": 3.5,
  "selected_count": 1,
  "tasks": [
    {
      "task": {
        "id": 1,
        "title": "Implement Binary Search Tree Balancing",
        "subject": "Data Structures & Algorithms",
        "estimated_effort": 3.5
      },
      "score": 122.6,
      "rationale": "Due soon (within 2 days) | Marked as Critical priority"
    }
  ],
  "efficiency_ratio": 100.0
}
```

---

## 3. Undo Engine (CO1 LIFO Stack)

### `GET /api/undo/peek`
Inspects the top action description without popping from the stack.

* **Response**: `200 OK`
```json
{
  "has_undo": true,
  "description": "Created task 'Graph Theory Practice Sheet' (#7)"
}
```

### `POST /api/undo`
Reverses the most recent action popped from the LIFO Stack in $\mathcal{O}(1)$ time.

* **Response**: `200 OK`
```json
{
  "success": true,
  "message": "Reverted creation: Removed task #7."
}
```

---

## 4. Examination & Schedule Management (CO3)

### `GET /api/exams`
Fetches all scheduled exams sorted using manual algorithms.

* **Query Parameters**:
  * `sort_by`: `date` | `subject` | `progress` (Default: `date`).
  * `algo`: `merge` | `insertion` | `bubble` (Default: `merge`).
  * `order`: `asc` | `desc` (Default: `asc`).
* **Response**: `200 OK`
```json
[
  {
    "id": 1,
    "subject": "Data Structures & Algorithms",
    "exam_date": "2026-10-31",
    "start_time": "09:30",
    "end_time": "12:30",
    "venue": "Exam Hall B-101",
    "syllabus": "Units 1-4: Stacks, Queues, Linked Lists, Trees, Sorting",
    "revision_progress": 70.0,
    "priority": "Critical"
  }
]
```

### `GET /api/exams/conflicts`
Runs interval collision detection to report clashing examination slots.

* **Response**: `200 OK`
```json
[
  {
    "date": "2026-11-15",
    "clashing_subjects": ["Data Structures & Algorithms", "Operating Systems"],
    "slot1": "Data Structures & Algorithms: 09:30 - 12:30 (Exam Hall B-101)",
    "slot2": "Operating Systems: 11:00 - 14:00 (Auditorium 2)",
    "severity": "Critical Clash"
  }
]
```

---

## 5. Academic Service Queue (CO1 FIFO Queue)

### `GET /api/requests`
Returns snapshots of pending requests in FIFO order and processed history.

* **Response**: `200 OK`
```json
{
  "pending": [
    {
      "id": 2,
      "request_id": "REQ-1002",
      "student_name": "Jerin",
      "request_type": "Re-evaluation",
      "subject": "Operating Systems",
      "details": "Question 4 (Semaphores) re-check",
      "status": "Pending",
      "created_at": "2026-10-27 20:30:00"
    }
  ],
  "history": []
}
```

### `POST /api/requests`
Enqueues a new service request at the rear of the queue in $\mathcal{O}(1)$ time.

* **Request Body**:
```json
{
  "student_name": "Alex Chen",
  "request_type": "Hall Ticket Generation",
  "subject": "Data Structures & Algorithms",
  "details": "Regular semester 3 hall ticket"
}
```
* **Response**: `201 Created`

### `POST /api/requests/process`
Dequeues and processes the next request in line from the front of the queue in strict $\mathcal{O}(1)$ time.

* **Response**: `200 OK`
```json
{
  "success": true,
  "message": "Processed request REQ-1002 (Re-evaluation) for Jerin in FIFO sequence.",
  "request": {
    "request_id": "REQ-1002",
    "status": "Processed"
  }
}
```

---

## 6. Academic Performance & Target Calculator

### `GET /api/performance`
Provides subject-by-subject averages, trend trajectory, and decline warnings.

* **Response**: `200 OK`
```json
{
  "overall_average": 75.8,
  "overall_grade": "A (Very Good)",
  "subjects": {
    "Operating Systems": {
      "subject": "Operating Systems",
      "assessment_count": 3,
      "average_percentage": 61.5,
      "status": "Proficient",
      "is_declining": true,
      "decline_reason": "Consecutive downward trend over last 3 assessments"
    }
  }
}
```

### `POST /api/performance/target-score`
Executes reverse sensitivity analysis to compute required marks on upcoming assessment.

* **Request Body**:
```json
{
  "subject": "Operating Systems",
  "target_average": 75.0,
  "upcoming_max_marks": 100.0,
  "upcoming_weightage": 30.0
}
```
* **Response**: `200 OK`
```json
{
  "subject": "Operating Systems",
  "current_average": 61.5,
  "target_average": 75.0,
  "required_marks": 88.5,
  "required_percentage": 88.5,
  "is_achievable": true,
  "advice": "Score at least 88.5 / 100.0 (88.5%) to hit your goal."
}
```

---

## 7. Academic Rescue Mode

### `GET /api/rescue`
Returns the systemic Crisis Index and top triage recommendations.

* **Response**: `200 OK`
```json
{
  "crisis_index": 43.0,
  "status_level": "Moderate Workload Warning",
  "action_statement": "Prioritize tasks due in the next 48 hours and reinforce vulnerable subjects.",
  "overdue_tasks_count": 1,
  "due_soon_count": 2,
  "vulnerable_subjects": ["Discrete Mathematics"],
  "imminent_exams_count": 1,
  "top_recommendations": []
}
```

---

## 8. DSA Performance Lab (CO2 & CO3)

### `POST /api/dsa/search`
Compares Linear Search (Array & Linked List) vs Binary Search across dataset of size $N$.

* **Request Body**: `{"size": 2000}`
* **Response**: `200 OK`
```json
{
  "dataset_size": 2000,
  "target": 98452,
  "linear_array": {
    "comparisons": 1708,
    "time_ms": 0.437,
    "complexity": "O(n)"
  },
  "linear_linked_list": {
    "comparisons": 1708,
    "time_ms": 0.615,
    "complexity": "O(n)"
  },
  "binary_search": {
    "comparisons": 11,
    "time_ms": 0.010,
    "complexity": "O(log n)"
  },
  "speedup_factor": 43.3
}
```

### `POST /api/dsa/sort`
Executes Bubble Sort, Insertion Sort, and Merge Sort on an identical randomized array.

* **Request Body**: `{"size": 500}`
* **Response**: `200 OK`
```json
{
  "dataset_size": 500,
  "bubble": { "time_ms": 15.2, "comparisons": 124750, "complexity": "O(n^2)" },
  "insertion": { "time_ms": 11.8, "comparisons": 62410, "complexity": "O(n^2)" },
  "merge": { "time_ms": 1.4, "comparisons": 4488, "complexity": "O(n log n)" }
}
```

### `POST /api/dsa/storage`
Empirical head insertion benchmark: Singly Linked List $\mathcal{O}(1)$ vs Python List $\mathcal{O}(n)$.

* **Request Body**: `{"size": 2000}`
* **Response**: `200 OK`
```json
{
  "dataset_size": 2000,
  "linked_list_head_insert_ms": 0.837,
  "array_head_insert_ms": 1.933,
  "speedup_ratio": 2.3,
  "explanation": "Inserting 2000 items at index 0 takes 0.84 ms in Linked List (O(1)) vs 1.93 ms in Array (O(n))."
}
```

---

## 9. System Configuration & Admin

### `POST /api/admin/reset-demo`
Wipes the SQLite database and reseeds standard dynamic demo datasets.

* **Response**: `200 OK` `{"success": true, "message": "Demo data reset successfully."}`

### `POST /api/admin/clear-data`
Empties all user records for a clean blank workspace.

* **Response**: `200 OK` `{"success": true, "message": "All workspace data cleared."}`
