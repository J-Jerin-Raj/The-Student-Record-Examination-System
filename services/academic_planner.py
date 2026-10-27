"""
Academic Planner Service.
Manages academic assignments and study tasks using SQLite persistence,
in-memory Singly Linked List (CO2) for sequential traversal,
and custom LIFO Stack (CO1) for undo operations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from models import Task, UndoAction
import database as db
from data_structures.stack import Stack
from data_structures.linked_list import SinglyLinkedList
from services.priority_engine import PriorityEngine


class AcademicPlannerService:
    """Manages tasks, multi-level undo, and daily study schedule optimization."""

    def __init__(self):
        self.undo_stack = Stack(capacity=100)
        self.task_linked_list = SinglyLinkedList()
        self.refresh_linked_list()

    def refresh_linked_list(self):
        """Sync in-memory Singly Linked List with database tasks."""
        self.task_linked_list.clear()
        tasks = db.get_all_tasks()
        for t in tasks:
            self.task_linked_list.insert_rear(t)

    def get_tasks(self, filter_status: Optional[str] = None, subject: Optional[str] = None) -> List[Task]:
        """Fetch all tasks with optional status and subject filtering."""
        tasks = db.get_all_tasks()
        if filter_status and filter_status != "All":
            tasks = [t for t in tasks if t.status == filter_status]
        if subject and subject != "All":
            tasks = [t for t in tasks if t.subject == subject]
        return tasks

    def add_task(self, task: Task, push_undo: bool = True) -> Tuple[bool, str, Optional[int]]:
        """Insert a new task into the database and push an undo token."""
        try:
            task_id = db.insert_task(task)
            task.id = task_id
            self.refresh_linked_list()

            if push_undo:
                self.undo_stack.push(
                    UndoAction(
                        entity_type="task",
                        action_type="CREATE",
                        entity_id=task_id,
                        previous_state=None,
                        new_state=task.to_dict(),
                        description=f"Created task '{task.title}'",
                    )
                )
            return True, f"Task '{task.title}' added successfully.", task_id
        except Exception as e:
            return False, f"Failed to add task: {str(e)}", None

    def update_task(self, task: Task, push_undo: bool = True) -> Tuple[bool, str]:
        """Update an existing task and save previous state on undo stack."""
        if task.id is None:
            return False, "Task ID is missing."

        old_task = db.get_task_by_id(task.id)
        if not old_task:
            return False, f"Task with ID {task.id} not found."

        try:
            success = db.update_task(task)
            if success:
                self.refresh_linked_list()
                if push_undo:
                    self.undo_stack.push(
                        UndoAction(
                            entity_type="task",
                            action_type="UPDATE",
                            entity_id=task.id,
                            previous_state=old_task.to_dict(),
                            new_state=task.to_dict(),
                            description=f"Updated task '{task.title}'",
                        )
                    )
                return True, f"Task '{task.title}' updated successfully."
            return False, "No changes applied."
        except Exception as e:
            return False, f"Update failed: {str(e)}"

    def delete_task(self, task_id: int, push_undo: bool = True) -> Tuple[bool, str]:
        """Delete task by ID and store snapshot on undo stack."""
        old_task = db.get_task_by_id(task_id)
        if not old_task:
            return False, f"Task with ID {task_id} not found."

        try:
            success = db.delete_task(task_id)
            if success:
                self.refresh_linked_list()
                if push_undo:
                    self.undo_stack.push(
                        UndoAction(
                            entity_type="task",
                            action_type="DELETE",
                            entity_id=task_id,
                            previous_state=old_task.to_dict(),
                            new_state=None,
                            description=f"Deleted task '{old_task.title}'",
                        )
                    )
                return True, f"Task '{old_task.title}' deleted successfully."
            return False, "Deletion failed."
        except Exception as e:
            return False, f"Error deleting task: {str(e)}"

    def toggle_status(self, task_id: int, new_status: str, push_undo: bool = True) -> Tuple[bool, str]:
        """Update status of a task (e.g. mark Completed or In Progress)."""
        task = db.get_task_by_id(task_id)
        if not task:
            return False, f"Task {task_id} not found."

        old_status = task.status
        task.status = new_status
        success = db.update_task(task)
        if success:
            self.refresh_linked_list()
            if push_undo:
                self.undo_stack.push(
                    UndoAction(
                        entity_type="task",
                        action_type="STATUS_CHANGE",
                        entity_id=task_id,
                        previous_state={"status": old_status},
                        new_state={"status": new_status},
                        description=f"Changed status of '{task.title}' from {old_status} to {new_status}",
                    )
                )
            return True, f"Status updated to {new_status}."
        return False, "Failed to update status."

    def undo_last_action(self) -> Tuple[bool, str]:
        """
        Pop the top action from the LIFO Undo Stack and reverse it.
        Time Complexity: O(1)
        """
        if self.undo_stack.is_empty():
            return False, "Undo stack is empty. No recent operations to revert."

        action: UndoAction = self.undo_stack.pop()

        if action.entity_type == "task":
            if action.action_type == "CREATE":
                # Revert create -> delete the task
                if action.entity_id is not None:
                    db.delete_task(action.entity_id)
                    self.refresh_linked_list()
                    return True, f"Reverted creation: Removed task ID {action.entity_id}."

            elif action.action_type == "DELETE":
                # Revert delete -> restore the task
                if action.previous_state:
                    restored_task = Task.from_dict(action.previous_state)
                    db.insert_task(restored_task)
                    self.refresh_linked_list()
                    return True, f"Reverted deletion: Restored task '{restored_task.title}'."

            elif action.action_type == "UPDATE":
                # Revert update -> restore previous field values
                if action.previous_state:
                    restored_task = Task.from_dict(action.previous_state)
                    db.update_task(restored_task)
                    self.refresh_linked_list()
                    return True, f"Reverted update: Restored previous version of '{restored_task.title}'."

            elif action.action_type == "STATUS_CHANGE":
                # Revert status toggle
                if action.entity_id and action.previous_state:
                    t = db.get_task_by_id(action.entity_id)
                    if t:
                        t.status = action.previous_state["status"]
                        db.update_task(t)
                        self.refresh_linked_list()
                        return True, f"Reverted status of '{t.title}' back to {t.status}."

        return False, f"Could not revert action '{action.description}'."

    def peek_undo(self) -> Optional[str]:
        """Inspect top action on the undo stack without popping."""
        action: Optional[UndoAction] = self.undo_stack.peek()
        return action.description if action else None

    def get_suggested_daily_schedule(
        self,
        available_hours: float,
        subject_averages: Optional[Dict[str, float]] = None,
        warning_threshold: float = 60.0,
    ) -> Dict[str, Any]:
        """
        Generates a transparent, rule-based daily study plan.
        Greedily selects the highest-priority pending tasks that fit within available_hours.
        """
        all_tasks = db.get_all_tasks()
        ranked = PriorityEngine.rank_tasks(
            all_tasks,
            subject_averages=subject_averages,
            warning_threshold=warning_threshold,
            include_completed=False,
        )

        selected_tasks = []
        allocated_hours = 0.0

        for item in ranked:
            t = item["task"]
            effort = t.estimated_effort
            if allocated_hours + effort <= available_hours + 0.5:  # Allow 30 min flexibility
                selected_tasks.append({
                    "task": t.to_dict(),
                    "score": item["score"],
                    "rationale": item["breakdown"].rationale,
                    "urgency_score": item["breakdown"].urgency_score,
                    "is_overdue": item["breakdown"].is_overdue,
                    "hours_remaining": item["breakdown"].hours_remaining,
                })
                allocated_hours += effort

        return {
            "available_hours": available_hours,
            "allocated_hours": round(allocated_hours, 1),
            "selected_count": len(selected_tasks),
            "tasks": selected_tasks,
            "efficiency_ratio": round((allocated_hours / max(0.1, available_hours)) * 100, 1),
        }

    def get_task_metrics(self) -> Dict[str, int]:
        """Calculate counts of tasks across status categories."""
        tasks = db.get_all_tasks()
        now = datetime.now()
        overdue_count = 0
        pending_count = 0
        in_progress_count = 0
        completed_count = 0

        for t in tasks:
            if t.status == "Completed":
                completed_count += 1
            else:
                if t.status == "In Progress":
                    in_progress_count += 1
                else:
                    pending_count += 1

                # Check if overdue
                try:
                    d_str = t.deadline.replace("T", " ")
                    if len(d_str) == 10:
                        d_str += " 23:59"
                    d_dt = datetime.strptime(d_str[:16], "%Y-%m-%d %H:%M")
                    if d_dt < now:
                        overdue_count += 1
                except Exception:
                    pass

        return {
            "total": len(tasks),
            "pending": pending_count,
            "in_progress": in_progress_count,
            "completed": completed_count,
            "overdue": overdue_count,
        }
