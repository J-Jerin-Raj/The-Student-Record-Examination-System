"""
Database Package for Acadence.
Exposes connection management, schema initialization, seeding, and CRUD operations.
"""

from database.connection import get_connection, DB_PATH
from database.schema import init_db, clear_all_data
from database.seed import seed_demo_data
from database.operations import (
    get_all_tasks,
    get_task_by_id,
    insert_task,
    update_task,
    delete_task,
    get_all_exams,
    get_exam_by_id,
    insert_exam,
    update_exam,
    delete_exam,
    get_all_assessments,
    insert_assessment,
    delete_assessment,
    get_all_requests,
    insert_academic_request,
    update_request_status,
    get_setting,
    set_setting,
    get_all_settings,
)

__all__ = [
    "get_connection",
    "DB_PATH",
    "init_db",
    "clear_all_data",
    "seed_demo_data",
    "get_all_tasks",
    "get_task_by_id",
    "insert_task",
    "update_task",
    "delete_task",
    "get_all_exams",
    "get_exam_by_id",
    "insert_exam",
    "update_exam",
    "delete_exam",
    "get_all_assessments",
    "insert_assessment",
    "delete_assessment",
    "get_all_requests",
    "insert_academic_request",
    "update_request_status",
    "get_setting",
    "set_setting",
    "get_all_settings",
]
