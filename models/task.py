"""
Task Model for Acadence.
Represents an academic assignment, project milestone, or study task.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Task:
    """Represents an academic assignment, project milestone, or study task."""
    id: Optional[int] = None
    title: str = ""
    subject: str = ""
    task_type: str = "Assignment"  # Assignment, Exam Prep, Project, Lab Work
    deadline: str = ""  # YYYY-MM-DDTHH:MM
    estimated_effort: float = 2.0  # Hours
    priority: str = "Medium"  # Critical, High, Medium, Low
    status: str = "Pending"  # Pending, In Progress, Completed
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        return cls(
            id=data.get("id"),
            title=data.get("title", ""),
            subject=data.get("subject", ""),
            task_type=data.get("task_type", "Assignment"),
            deadline=data.get("deadline", ""),
            estimated_effort=float(data.get("estimated_effort", 2.0)),
            priority=data.get("priority", "Medium"),
            status=data.get("status", "Pending"),
            notes=data.get("notes", ""),
            created_at=data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
