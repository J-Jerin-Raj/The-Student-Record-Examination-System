"""
Database Schema Initialization and Reset for Acadence.
Creates tables and provides clean teardown functions.
"""

import sqlite3
from typing import Optional
from database.connection import get_connection
from database.seed import seed_demo_data


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
