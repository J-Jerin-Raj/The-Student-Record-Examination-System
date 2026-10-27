"""
SQLite Database Layer for Acadence.
Provides persistent storage, schema initialization, CRUD operations,
and sample demo data seeding / reset capabilities.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from models import Task, Exam, Assessment, AcademicRequest

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "acadence.db")


def get_connection() -> sqlite3.Connection:
    """Establish connection with row factory configured."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create database tables if they do not exist and seed initial demo data."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        subject TEXT NOT NULL,
        task_type TEXT NOT NULL,
        deadline TEXT NOT NULL,
        estimated_effort REAL NOT NULL,
        priority TEXT NOT NULL,
        status TEXT NOT NULL,
        notes TEXT,
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        exam_date TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        venue TEXT NOT NULL,
        syllabus TEXT,
        revision_progress REAL NOT NULL,
        priority TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        assessment_name TEXT NOT NULL,
        assessment_type TEXT NOT NULL,
        max_marks REAL NOT NULL,
        marks_obtained REAL NOT NULL,
        weightage REAL NOT NULL,
        assessment_date TEXT NOT NULL,
        notes TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS academic_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id TEXT NOT NULL UNIQUE,
        student_name TEXT NOT NULL,
        request_type TEXT NOT NULL,
        subject TEXT NOT NULL,
        details TEXT,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """)

    conn.commit()

    # Check if empty, if so, seed demo data
    cursor.execute("SELECT COUNT(*) as count FROM tasks")
    row = cursor.fetchone()
    if row and row["count"] == 0:
        seed_demo_data(conn)

    conn.close()


def seed_demo_data(conn: Optional[sqlite3.Connection] = None):
    """Seed realistic student academic data with relative dates for immediate relevance."""
    close_conn = False
    if conn is None:
        conn = get_connection()
        close_conn = True

    cursor = conn.cursor()
    now = datetime.now()

    # 1. Tasks
    demo_tasks = [
        (
            "Implement Binary Search Tree Balancing",
            "Data Structures & Algorithms",
            "Assignment",
            (now + timedelta(days=1, hours=4)).strftime("%Y-%m-%d %H:%M"),
            3.5,
            "Critical",
            "In Progress",
            "Need to complete AVL tree rotations and test edge cases.",
            (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "REST API Authentication & JWT Middleware",
            "Web Development",
            "Project",
            (now + timedelta(days=3)).strftime("%Y-%m-%d %H:%M"),
            4.0,
            "High",
            "Pending",
            "Integrate token expiration handling and secure route guards.",
            (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "Process Scheduling Simulation Lab Report",
            "Operating Systems",
            "Lab Work",
            (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),  # Overdue task!
            2.5,
            "Critical",
            "Pending",
            "Compare Round Robin vs Shortest Job First turnaround times.",
            (now - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "Graph Theory Proofs Practice Sheet",
            "Discrete Mathematics",
            "Assignment",
            (now + timedelta(days=5)).strftime("%Y-%m-%d %H:%M"),
            3.0,
            "Medium",
            "Pending",
            "Solve Euler path and Hamiltonian circuit problems.",
            (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "SQL Normalization & BCNF Decomposition",
            "Database Management Systems",
            "Assignment",
            (now + timedelta(days=7)).strftime("%Y-%m-%d %H:%M"),
            2.0,
            "Medium",
            "Pending",
            "Convert 3NF relations to BCNF and eliminate functional anomalies.",
            (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "CSS Grid & Flexbox Responsive Portfolio",
            "Web Development",
            "Assignment",
            (now - timedelta(days=5)).strftime("%Y-%m-%d %H:%M"),
            2.0,
            "Low",
            "Completed",
            "Submitted on university portal.",
            (now - timedelta(days=8)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
    ]

    cursor.executemany("""
    INSERT INTO tasks (title, subject, task_type, deadline, estimated_effort, priority, status, notes, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, demo_tasks)

    # 2. Exams
    demo_exams = [
        (
            "Data Structures & Algorithms",
            (now + timedelta(days=4)).strftime("%Y-%m-%d"),
            "09:30",
            "12:30",
            "Exam Hall B-101",
            "Units 1-4: Stacks, Queues, Linked Lists, Trees, Sorting, and Graphs.",
            70.0,
            "Critical",
            (now - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "Operating Systems",
            (now + timedelta(days=8)).strftime("%Y-%m-%d"),
            "14:00",
            "17:00",
            "Auditorium 2",
            "Processes, Threads, CPU Scheduling, Deadlocks, Virtual Memory.",
            45.0,
            "High",
            (now - timedelta(days=9)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "Web Development",
            (now + timedelta(days=12)).strftime("%Y-%m-%d"),
            "09:30",
            "12:30",
            "Computer Lab 3",
            "Frontend HTML/CSS/JS, Backend Python REST APIs, Security, Deployment.",
            80.0,
            "Medium",
            (now - timedelta(days=8)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "Discrete Mathematics",
            (now + timedelta(days=16)).strftime("%Y-%m-%d"),
            "14:00",
            "17:00",
            "Exam Hall A-204",
            "Set Theory, Relations, Graph Theory, Combinatorics, Recurrence.",
            35.0,
            "Critical",
            (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
    ]

    cursor.executemany("""
    INSERT INTO exams (subject, exam_date, start_time, end_time, venue, syllabus, revision_progress, priority, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, demo_exams)

    # 3. Assessments
    demo_assessments = [
        # DSA: Strong performance
        ("Data Structures & Algorithms", "Quiz 1 (Arrays & Complexity)", "Quiz", 20.0, 18.5, 10.0, (now - timedelta(days=30)).strftime("%Y-%m-%d"), "Solid grasp of Big-O."),
        ("Data Structures & Algorithms", "Mid-Term Examination", "Internal", 50.0, 44.0, 25.0, (now - timedelta(days=15)).strftime("%Y-%m-%d"), "Well done on stacks and queues."),
        ("Data Structures & Algorithms", "Lab Practical 1", "Lab", 30.0, 27.5, 15.0, (now - timedelta(days=5)).strftime("%Y-%m-%d"), "Linked list implementations."),

        # WebDev: Strong performance
        ("Web Development", "Assignment 1 (Responsive Design)", "Assignment", 25.0, 23.5, 15.0, (now - timedelta(days=28)).strftime("%Y-%m-%d"), "Good semantic HTML."),
        ("Web Development", "Mid-Term Examination", "Internal", 50.0, 42.0, 25.0, (now - timedelta(days=14)).strftime("%Y-%m-%d"), "Client-server architecture."),

        # Operating Systems: Declining / Vulnerable performance
        ("Operating Systems", "Quiz 1 (Architecture)", "Quiz", 20.0, 16.0, 10.0, (now - timedelta(days=32)).strftime("%Y-%m-%d"), "Good on system calls."),
        ("Operating Systems", "Mid-Term Examination", "Internal", 50.0, 28.5, 25.0, (now - timedelta(days=12)).strftime("%Y-%m-%d"), "Struggled with synchronization & semaphores."),
        ("Operating Systems", "Process Sync Quiz", "Quiz", 20.0, 9.5, 10.0, (now - timedelta(days=4)).strftime("%Y-%m-%d"), "Needs serious revision on deadlocks and Peterson's algorithm."),

        # Discrete Mathematics: Critical performance
        ("Discrete Mathematics", "Quiz 1 (Set Theory)", "Quiz", 20.0, 14.0, 10.0, (now - timedelta(days=26)).strftime("%Y-%m-%d"), "Acceptable."),
        ("Discrete Mathematics", "Mid-Term Examination", "Internal", 50.0, 23.0, 25.0, (now - timedelta(days=10)).strftime("%Y-%m-%d"), "Below 50% threshold. Recurrence relations need work."),

        # DBMS: Moderate performance
        ("Database Management Systems", "Quiz 1 (Relational Algebra)", "Quiz", 20.0, 17.0, 10.0, (now - timedelta(days=22)).strftime("%Y-%m-%d"), "Good query writing."),
        ("Database Management Systems", "Mid-Term Examination", "Internal", 50.0, 36.0, 25.0, (now - timedelta(days=8)).strftime("%Y-%m-%d"), "Need to improve normalization proofs."),
    ]

    cursor.executemany("""
    INSERT INTO assessments (subject, assessment_name, assessment_type, max_marks, marks_obtained, weightage, assessment_date, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, demo_assessments)

    # 4. Academic Requests
    demo_requests = [
        ("REQ-1001", "Jerin", "Hall Ticket Generation", "Data Structures & Algorithms", "Semester 3 Regular Hall Ticket", "Processed", (now - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S")),
        ("REQ-1002", "Jerin", "Re-evaluation", "Operating Systems", "Mid-Term Question 4 (Semaphores) re-check requested", "Pending", (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")),
        ("REQ-1003", "Jerin", "Doubt Session", "Discrete Mathematics", "Request 1-on-1 tutoring on generating functions", "Pending", (now - timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S")),
    ]

    cursor.executemany("""
    INSERT INTO academic_requests (request_id, student_name, request_type, subject, details, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, demo_requests)

    # 5. Default Settings
    settings_pairs = [
        ("warning_threshold", "60.0"),
        ("target_percentage", "80.0"),
        ("daily_study_hours", "3.5"),
        ("theme", "dark"),
        ("student_name", "Alex Chen"),
        ("degree_program", "B.Tech Computer Science & Engineering (Semester 3)"),
    ]
    cursor.executemany("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", settings_pairs)

    conn.commit()
    if close_conn:
        conn.close()


def clear_all_data():
    """Clear all records from database for a fresh workspace."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks")
    cursor.execute("DELETE FROM exams")
    cursor.execute("DELETE FROM assessments")
    cursor.execute("DELETE FROM academic_requests")
    conn.commit()
    conn.close()


# ------------------ Task DB Operations ------------------

def get_all_tasks() -> List[Task]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY deadline ASC")
    rows = cursor.fetchall()
    tasks = [Task.from_dict(dict(r)) for r in rows]
    conn.close()
    return tasks


def get_task_by_id(task_id: int) -> Optional[Task]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    return Task.from_dict(dict(row)) if row else None


def insert_task(task: Task) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO tasks (title, subject, task_type, deadline, estimated_effort, priority, status, notes, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task.title,
        task.subject,
        task.task_type,
        task.deadline,
        task.estimated_effort,
        task.priority,
        task.status,
        task.notes,
        task.created_at,
    ))
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id


def update_task(task: Task) -> bool:
    if task.id is None:
        return False
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE tasks
    SET title = ?, subject = ?, task_type = ?, deadline = ?, estimated_effort = ?,
        priority = ?, status = ?, notes = ?
    WHERE id = ?
    """, (
        task.title,
        task.subject,
        task.task_type,
        task.deadline,
        task.estimated_effort,
        task.priority,
        task.status,
        task.notes,
        task.id,
    ))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected


def delete_task(task_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected


# ------------------ Exam DB Operations ------------------

def get_all_exams() -> List[Exam]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exams ORDER BY exam_date ASC, start_time ASC")
    rows = cursor.fetchall()
    exams = [Exam.from_dict(dict(r)) for r in rows]
    conn.close()
    return exams


def get_exam_by_id(exam_id: int) -> Optional[Exam]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exams WHERE id = ?", (exam_id,))
    row = cursor.fetchone()
    conn.close()
    return Exam.from_dict(dict(row)) if row else None


def insert_exam(exam: Exam) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO exams (subject, exam_date, start_time, end_time, venue, syllabus, revision_progress, priority, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        exam.subject,
        exam.exam_date,
        exam.start_time,
        exam.end_time,
        exam.venue,
        exam.syllabus,
        exam.revision_progress,
        exam.priority,
        exam.created_at,
    ))
    exam_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return exam_id


def update_exam(exam: Exam) -> bool:
    if exam.id is None:
        return False
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE exams
    SET subject = ?, exam_date = ?, start_time = ?, end_time = ?, venue = ?,
        syllabus = ?, revision_progress = ?, priority = ?
    WHERE id = ?
    """, (
        exam.subject,
        exam.exam_date,
        exam.start_time,
        exam.end_time,
        exam.venue,
        exam.syllabus,
        exam.revision_progress,
        exam.priority,
        exam.id,
    ))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected


def delete_exam(exam_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected


# ------------------ Assessment DB Operations ------------------

def get_all_assessments() -> List[Assessment]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assessments ORDER BY assessment_date ASC")
    rows = cursor.fetchall()
    assessments = [Assessment.from_dict(dict(r)) for r in rows]
    conn.close()
    return assessments


def insert_assessment(assessment: Assessment) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO assessments (subject, assessment_name, assessment_type, max_marks, marks_obtained, weightage, assessment_date, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        assessment.subject,
        assessment.assessment_name,
        assessment.assessment_type,
        assessment.max_marks,
        assessment.marks_obtained,
        assessment.weightage,
        assessment.assessment_date,
        assessment.notes,
    ))
    aid = cursor.lastrowid
    conn.commit()
    conn.close()
    return aid


def delete_assessment(assessment_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assessments WHERE id = ?", (assessment_id,))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected


# ------------------ Academic Requests DB Operations ------------------

def get_all_requests() -> List[AcademicRequest]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM academic_requests ORDER BY id ASC")
    rows = cursor.fetchall()
    reqs = [
        AcademicRequest(
            id=r["id"],
            request_id=r["request_id"],
            student_name=r["student_name"],
            request_type=r["request_type"],
            subject=r["subject"],
            details=r["details"],
            status=r["status"],
            created_at=r["created_at"],
        )
        for r in rows
    ]
    conn.close()
    return reqs


def insert_academic_request(req: AcademicRequest) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO academic_requests (request_id, student_name, request_type, subject, details, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        req.request_id,
        req.student_name,
        req.request_type,
        req.subject,
        req.details,
        req.status,
        req.created_at,
    ))
    rid = cursor.lastrowid
    conn.commit()
    conn.close()
    return rid


def update_request_status(request_id: str, new_status: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE academic_requests SET status = ? WHERE request_id = ?", (new_status, request_id))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected


# ------------------ Settings DB Operations ------------------

def get_setting(key: str, default: str = "") -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key: str, value: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()


def get_all_settings() -> Dict[str, str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    rows = cursor.fetchall()
    res = {r["key"]: r["value"] for r in rows}
    conn.close()
    return res
