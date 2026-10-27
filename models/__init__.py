"""
Data Models for Acadence.
Defines structured dataclasses representing tasks, exams, assessments, and undo actions.
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


@dataclass
class Exam:
    """Represents an upcoming or scheduled examination."""
    id: Optional[int] = None
    subject: str = ""
    exam_date: str = ""  # YYYY-MM-DD
    start_time: str = "09:30"  # HH:MM
    end_time: str = "12:30"  # HH:MM
    venue: str = "Hall A"
    syllabus: str = ""
    revision_progress: float = 0.0  # 0 to 100%
    priority: str = "High"  # Critical, High, Medium, Low
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Exam":
        return cls(
            id=data.get("id"),
            subject=data.get("subject", ""),
            exam_date=data.get("exam_date", ""),
            start_time=data.get("start_time", "09:30"),
            end_time=data.get("end_time", "12:30"),
            venue=data.get("venue", "Hall A"),
            syllabus=data.get("syllabus", ""),
            revision_progress=float(data.get("revision_progress", 0.0)),
            priority=data.get("priority", "High"),
            created_at=data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )


@dataclass
class Assessment:
    """Represents a student assessment score (quiz, test, assignment, or final)."""
    id: Optional[int] = None
    subject: str = ""
    assessment_name: str = ""
    assessment_type: str = "Internal"  # Quiz, Assignment, Internal, Lab, Final
    max_marks: float = 100.0
    marks_obtained: float = 0.0
    weightage: float = 20.0  # Percentage weight
    assessment_date: str = ""  # YYYY-MM-DD
    notes: str = ""

    @property
    def percentage(self) -> float:
        if self.max_marks <= 0:
            return 0.0
        return round((self.marks_obtained / self.max_marks) * 100.0, 2)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["percentage"] = self.percentage
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Assessment":
        return cls(
            id=data.get("id"),
            subject=data.get("subject", ""),
            assessment_name=data.get("assessment_name", ""),
            assessment_type=data.get("assessment_type", "Internal"),
            max_marks=float(data.get("max_marks", 100.0)),
            marks_obtained=float(data.get("marks_obtained", 0.0)),
            weightage=float(data.get("weightage", 20.0)),
            assessment_date=data.get("assessment_date", datetime.now().strftime("%Y-%m-%d")),
            notes=data.get("notes", ""),
        )


@dataclass
class AcademicRequest:
    """Represents a student academic service request managed in FIFO Queue."""
    id: Optional[int] = None
    request_id: str = ""
    student_name: str = "Student"
    request_type: str = "Re-evaluation"  # Hall Ticket, Re-evaluation, Doubt Session, Transcript
    subject: str = ""
    details: str = ""
    status: str = "Pending"  # Pending, Processed
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UndoAction:
    """Represents an invertible action token stored in the LIFO Undo Stack."""
    entity_type: str  # 'task', 'exam', 'assessment'
    action_type: str  # 'CREATE', 'UPDATE', 'DELETE', 'STATUS_CHANGE'
    entity_id: Optional[int] = None
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    description: str = ""


@dataclass
class Student:
    """Represents student academic profile details."""
    student_id: str = "STU101"
    name: str = "Alex Chen"
    department: str = "Computer Science & Engineering"
    semester: int = 3
    marks: Dict[str, float] = field(default_factory=dict)

    @property
    def percentage(self) -> float:
        if not self.marks:
            return 0.0
        return round(sum(self.marks.values()) / (len(self.marks) * 100.0) * 100.0, 2)

    @property
    def grade(self) -> str:
        pct = self.percentage
        if pct >= 90:
            return "O (Outstanding)"
        elif pct >= 80:
            return "A+ (Excellent)"
        elif pct >= 70:
            return "A (Very Good)"
        elif pct >= 60:
            return "B+ (Good)"
        elif pct >= 50:
            return "B (Above Average)"
        elif pct >= 40:
            return "C (Pass)"
        else:
            return "F (Fail)"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "department": self.department,
            "semester": self.semester,
            "marks": self.marks,
            "percentage": self.percentage,
            "grade": self.grade,
        }

