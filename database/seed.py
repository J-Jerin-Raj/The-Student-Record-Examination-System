"""
Database Seed Operations for Acadence.
Seeds realistic student academic data with relative dates for immediate relevance.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional
from database.connection import get_connection


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
