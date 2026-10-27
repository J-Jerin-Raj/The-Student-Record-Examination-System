"""
Student Manager Service.
Integrates Singly Linked List (CO2) for core student record storage,
and a Stack (CO1) for robust multi-level Undo functionality.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import json
import os

from structures.linked_list import SinglyLinkedList
from structures.stack import Stack
from models.student import Student


@dataclass
class UndoAction:
    """Represents a reversible modification action for the undo stack."""
    action_type: str  # 'ADD', 'UPDATE', 'DELETE'
    student_id: str
    previous_state: Optional[Student] = None
    new_state: Optional[Student] = None
    description: str = ""


class StudentManager:
    """
    Manages student records using a Singly Linked List as the primary data store
    and a custom Stack to record reversible operations (Undo).
    """

    def __init__(self):
        self.records = SinglyLinkedList()
        self.undo_stack = Stack(capacity=100)

    def add_student(self, student: Student, push_undo: bool = True) -> Tuple[bool, str]:
        """
        Add a new student to the linked list.
        Prevents duplicate student IDs.
        Pushes an ADD action to the undo stack.
        """
        existing, _ = self.records.search_by_id(student.student_id)
        if existing is not None:
            return False, f"Student with ID '{student.student_id}' already exists."

        # Insert at end of linked list
        self.records.insert_at_end(student)

        if push_undo:
            action = UndoAction(
                action_type="ADD",
                student_id=student.student_id,
                new_state=student.copy(),
                description=f"Added student {student.name} ({student.student_id})",
            )
            self.undo_stack.push(action)

        return True, f"Student '{student.name}' added successfully."

    def update_student(
        self, student_id: str, updated_student: Student, push_undo: bool = True
    ) -> Tuple[bool, str]:
        """
        Update an existing student's record.
        Saves previous state on the undo stack.
        """
        success, old_data = self.records.update_by_id(student_id, updated_student)
        if not success or old_data is None:
            return False, f"Student with ID '{student_id}' not found."

        if push_undo:
            action = UndoAction(
                action_type="UPDATE",
                student_id=student_id,
                previous_state=old_data.copy(),
                new_state=updated_student.copy(),
                description=f"Updated details of {updated_student.name} ({student_id})",
            )
            self.undo_stack.push(action)

        return True, f"Student '{student_id}' updated successfully."

    def delete_student(self, student_id: str, push_undo: bool = True) -> Tuple[bool, str]:
        """
        Delete a student from the linked list.
        Saves deleted student data to the undo stack.
        """
        deleted_student, _ = self.records.delete_by_id(student_id)
        if deleted_student is None:
            return False, f"Student with ID '{student_id}' not found."

        if push_undo:
            action = UndoAction(
                action_type="DELETE",
                student_id=student_id,
                previous_state=deleted_student.copy(),
                description=f"Deleted student {deleted_student.name} ({student_id})",
            )
            self.undo_stack.push(action)

        return True, f"Student '{deleted_student.name}' deleted successfully."

    def undo_last_action(self) -> Tuple[bool, str]:
        """
        Reverses the most recent action popped from the LIFO Undo Stack.
        - Undoing ADD: deletes the newly added student.
        - Undoing DELETE: restores the deleted student to the linked list.
        - Undoing UPDATE: restores previous student data.
        """
        if self.undo_stack.is_empty():
            return False, "Undo stack is empty. No recent operations to revert."

        last_action: UndoAction = self.undo_stack.pop()

        if last_action.action_type == "ADD":
            # Reverse ADD -> Delete without pushing another undo
            self.records.delete_by_id(last_action.student_id)
            return True, f"Reverted ADD: Removed student {last_action.student_id}."

        elif last_action.action_type == "DELETE":
            # Reverse DELETE -> Re-insert the previous state
            if last_action.previous_state:
                self.records.insert_at_end(last_action.previous_state)
                return True, (
                    f"Reverted DELETE: Restored student "
                    f"{last_action.previous_state.name} ({last_action.student_id})."
                )
            return False, "Failed to restore: Missing snapshot data."

        elif last_action.action_type == "UPDATE":
            # Reverse UPDATE -> Restore old state
            if last_action.previous_state:
                self.records.update_by_id(last_action.student_id, last_action.previous_state)
                return True, (
                    f"Reverted UPDATE: Restored previous record for "
                    f"{last_action.previous_state.name} ({last_action.student_id})."
                )
            return False, "Failed to restore: Missing snapshot data."

        return False, f"Unknown action type '{last_action.action_type}'."

    def peek_undo(self) -> Optional[str]:
        """Inspect the top action description on the undo stack without popping."""
        action = self.undo_stack.peek()
        if action:
            return action.description
        return None

    def get_student_by_id(self, student_id: str) -> Optional[Student]:
        """Retrieve a student by ID using linked list linear search."""
        student, _ = self.records.search_by_id(student_id)
        return student

    def get_all_students(self) -> List[Student]:
        """Return all student records as a Python list."""
        return self.records.to_list()

    def count(self) -> int:
        """Return total number of student records."""
        return len(self.records)

    def load_from_json(self, filepath: str) -> int:
        """Load student records from a JSON file into the linked list."""
        if not os.path.exists(filepath):
            return 0

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        loaded = 0
        for item in data:
            student = Student.from_dict(item)
            success, _ = self.add_student(student, push_undo=False)
            if success:
                loaded += 1
        return loaded

    def save_to_json(self, filepath: str) -> None:
        """Export all current student records to a JSON file."""
        students = self.get_all_students()
        data = [s.to_dict() for s in students]
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
