"""
Database CRUD Operations for Acadence.
Provides queries and persistence for tasks, exams, assessments, requests, and settings.
"""

from typing import Dict, List, Optional
from models.task import Task
from models.exam import Exam
from models.assessment import Assessment
from models.request import AcademicRequest
from database.connection import get_connection


# ------------------ Task DB Operations ------------------

def get_all_tasks() -> List[Task]:
    """Retrieve all tasks sorted by deadline ascending."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY deadline ASC")
    rows = cursor.fetchall()
    tasks = [Task.from_dict(dict(r)) for r in rows]
    conn.close()
    return tasks


def get_task_by_id(task_id: int) -> Optional[Task]:
    """Retrieve an individual task by integer primary key."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    return Task.from_dict(dict(row)) if row else None


def insert_task(task: Task) -> int:
    """Insert a new task into database and return its primary key id."""
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
    """Update existing task fields by id."""
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
    """Delete a task record by id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected


# ------------------ Exam DB Operations ------------------

def get_all_exams() -> List[Exam]:
    """Retrieve all exams sorted by date and start time ascending."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exams ORDER BY exam_date ASC, start_time ASC")
    rows = cursor.fetchall()
    exams = [Exam.from_dict(dict(r)) for r in rows]
    conn.close()
    return exams


def get_exam_by_id(exam_id: int) -> Optional[Exam]:
    """Retrieve an exam by id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exams WHERE id = ?", (exam_id,))
    row = cursor.fetchone()
    conn.close()
    return Exam.from_dict(dict(row)) if row else None


def insert_exam(exam: Exam) -> int:
    """Insert a new exam and return its id."""
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
    """Update an existing exam by id."""
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
    """Delete an exam by id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected


# ------------------ Assessment DB Operations ------------------

def get_all_assessments() -> List[Assessment]:
    """Retrieve all assessments ordered by date ascending."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assessments ORDER BY assessment_date ASC")
    rows = cursor.fetchall()
    assessments = [Assessment.from_dict(dict(r)) for r in rows]
    conn.close()
    return assessments


def insert_assessment(assessment: Assessment) -> int:
    """Insert an assessment record and return its id."""
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
    """Delete an assessment by id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assessments WHERE id = ?", (assessment_id,))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected


# ------------------ Academic Requests DB Operations ------------------

def get_all_requests() -> List[AcademicRequest]:
    """Retrieve all student academic requests ordered by id ascending."""
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
    """Insert an academic service request."""
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
    """Update status of an academic service request."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE academic_requests SET status = ? WHERE request_id = ?", (new_status, request_id))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected


# ------------------ Settings DB Operations ------------------

def get_setting(key: str, default: str = "") -> str:
    """Retrieve string setting value by key."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key: str, value: str):
    """Upsert setting key-value pair."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()


def get_all_settings() -> Dict[str, str]:
    """Retrieve all key-value settings as a dictionary."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    rows = cursor.fetchall()
    res = {r["key"]: r["value"] for r in rows}
    conn.close()
    return res
